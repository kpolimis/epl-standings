#!/usr/bin/env python3
"""Build verified EPL standings from two authoritative sources.

PRIMARY SOURCE (1993/94 – present):
  football-data.co.uk — Joseph Buchdahl's match results database.

SECONDARY SOURCE (1991/92 First Division + 1992/93 inaugural EPL only):
  jalapic/engsoccerdata — used solely to fill seasons football-data
  doesn't cover.

Final tables are derived from match results: points → GD → GF, with
alphabetical as the final tiebreaker. A small CORRECTIONS dict overrides
positions in seasons where off-pitch adjustments (points deductions, etc.)
cannot be derived from scores alone.

Caching: fetched URLs are cached under data/cache/ keyed by URL hash.
Use --refresh to ignore the cache and re-fetch.

Exit codes:
    0  — every season fetched and validated
    1  — any fetch failed or validation found bad positions
"""
import argparse
import csv
import hashlib
import io
import json
import logging
import os
import sys
import urllib.request
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

CACHE_DIR = "data/cache"


def _cache_path(url: str) -> str:
    return os.path.join(CACHE_DIR, hashlib.sha1(url.encode()).hexdigest())


def fetch(url: str, use_cache: bool = True) -> str:
    """Fetch URL content as text, with on-disk caching keyed by URL hash."""
    cache_file = _cache_path(url)
    if use_cache and os.path.exists(cache_file):
        with open(cache_file, encoding="utf-8") as f:
            return f.read()
    req = urllib.request.Request(url, headers={"User-Agent": "EPL-standings-fetcher/1.0"})
    with urllib.request.urlopen(req, timeout=20) as response:
        body = response.read().decode("utf-8", errors="replace")
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(cache_file, "w", encoding="utf-8") as f:
        f.write(body)
    return body


def build_table(matches: list[tuple[str, str, int, int]]) -> dict[str, int] | None:
    """Derive a final league table from match results.

    Tiebreakers: points → goal difference → goals scored → alphabetical.
    Returns None if no matches were provided.
    """
    pts = defaultdict(int)
    gf  = defaultdict(int)
    ga  = defaultdict(int)

    for home, away, hg, ag in matches:
        gf[home] += hg; ga[home] += ag
        gf[away] += ag; ga[away] += hg
        if   hg > ag: pts[home] += 3
        elif hg < ag: pts[away] += 3
        else:         pts[home] += 1; pts[away] += 1

    if not pts:
        return None

    ranked = sorted(pts.keys(), key=lambda t: (-pts[t], -(gf[t] - ga[t]), -gf[t], t))
    return {team: pos + 1 for pos, team in enumerate(ranked)}


NAMES = {
    "Man United":      "Manchester United",
    "Man City":        "Manchester City",
    "Tottenham":       "Tottenham Hotspur",
    "Spurs":           "Tottenham Hotspur",
    "Newcastle":       "Newcastle United",
    "Leicester":       "Leicester City",
    "Leeds":           "Leeds United",
    "Wolves":          "Wolverhampton Wanderers",
    "West Ham":        "West Ham United",
    "Sheffield Weds":  "Sheffield Wednesday",
    "Sheffield Wed":   "Sheffield Wednesday",
    "Sheff Wed":       "Sheffield Wednesday",
    "Sheffield Utd":   "Sheffield United",
    "Sheff United":    "Sheffield United",
    "Sheff Utd":       "Sheffield United",
    "Nott'm Forest":   "Nottingham Forest",
    "Nottm Forest":    "Nottingham Forest",
    "Notts Forest":    "Nottingham Forest",
    "Nott'm For":      "Nottingham Forest",
    "Brighton":        "Brighton & Hove Albion",
    "Bournemouth":     "Bournemouth",
    "Blackburn":       "Blackburn Rovers",
    "Bolton":          "Bolton Wanderers",
    "West Brom":       "West Brom",
    "WBA":             "West Brom",
    "Cardiff":         "Cardiff City",
    "Swansea":         "Swansea City",
    "Stoke":           "Stoke City",
    "Huddersfield":    "Huddersfield Town",
    "Coventry":        "Coventry City",
    "Charlton":        "Charlton Athletic",
    "Wimbledon":       "Wimbledon",
    "Swindon":         "Swindon Town",
    "Oldham":          "Oldham Athletic",
    "Ipswich":         "Ipswich Town",
    "Derby":           "Derby County",
    "Middlesbrough":   "Middlesbrough",
    "Bradford":        "Bradford City",
    "Watford":         "Watford",
    "Burnley":         "Burnley",
    "Fulham":          "Fulham",
    "Hull":            "Hull City",
    "Reading":         "Reading",
    "Wigan":           "Wigan Athletic",
    "QPR":             "QPR",
    "Queens Park Rangers": "QPR",
    "Blackpool":       "Blackpool",
    "Birmingham":      "Birmingham City",
    "Portsmouth":      "Portsmouth",
    "Norwich":         "Norwich City",
    "Sunderland":      "Sunderland",
    "Brentford":       "Brentford",
    "Luton":           "Luton Town",
    "Barnsley":        "Barnsley",
}


# Off-pitch adjustments invisible to match results.
CORRECTIONS = {
    "1996/97": {
        # Middlesbrough deducted 3pts for failing to fulfil fixture at Blackburn.
        "Middlesbrough":  19,
        "West Ham United": 14,
        "Everton":        15,
        "Southampton":    16,
        "Coventry City":  17,
        "Sunderland":     18,
    },
}


def norm(name: str) -> str:
    """Normalise a team name to its canonical form."""
    return NAMES.get(name.strip(), name.strip())


def fetch_primary(use_cache: bool) -> tuple[dict[str, dict[str, int]], list[str]]:
    """Fetch football-data.co.uk seasons. Returns (data, failed_seasons)."""
    logger.info("=" * 62)
    logger.info("PRIMARY: football-data.co.uk  (1993/94 – 2025/26)")
    logger.info("=" * 62)

    base = "https://www.football-data.co.uk/mmz4281"
    data: dict[str, dict[str, int]] = {}
    failed: list[str] = []

    for year in range(1993, 2026):
        season = f"{year}/{str(year+1)[2:]}"
        code = f"{str(year)[2:]}{str(year+1)[2:]}"
        url = f"{base}/{code}/E0.csv"
        try:
            raw = fetch(url, use_cache=use_cache)
            reader = csv.DictReader(io.StringIO(raw))
            matches = []
            for row in reader:
                try:
                    matches.append((norm(row["HomeTeam"]), norm(row["AwayTeam"]),
                                    int(row["FTHG"]), int(row["FTAG"])))
                except (KeyError, ValueError):
                    continue
            table = build_table(matches)
            if not table:
                logger.warning(f"  ✗ {season}: no valid matches")
                failed.append(season)
                continue
            data[season] = table
            logger.info(f"  ✓ {season}: {len(table)} teams  champion: {min(table, key=table.get)}")
        except Exception as e:
            logger.error(f"  ✗ {season}: {e}")
            failed.append(season)

    return data, failed


def fetch_secondary(use_cache: bool) -> tuple[dict[str, dict[str, int]], list[str]]:
    """Fetch jalapic 1991/92 + 1992/93. Returns (data, failed_seasons)."""
    logger.info("")
    logger.info("=" * 62)
    logger.info("SECONDARY: jalapic/engsoccerdata  (1991/92 + 1992/93 only)")
    logger.info("=" * 62)

    url = ("https://raw.githubusercontent.com/jalapic/engsoccerdata"
           "/master/data-raw/england.csv")
    data: dict[str, dict[str, int]] = {}
    failed: list[str] = []

    try:
        raw = fetch(url, use_cache=use_cache)
        all_rows = list(csv.DictReader(io.StringIO(raw)))
        logger.info(f"  Downloaded {len(all_rows)} match records")
    except Exception as e:
        logger.error(f"  ✗ jalapic fetch failed: {e}")
        return data, ["1991/92 (First Div.)", "1992/93"]

    for year, label in [(1991, "1991/92 (First Div.)"), (1992, "1992/93")]:
        rows = [r for r in all_rows
                if r.get("Season") == str(year) and r.get("tier", "") == "1"]
        matches = []
        for row in rows:
            try:
                matches.append((norm(row["home"]), norm(row["visitor"]),
                                int(row["hgoal"]), int(row["vgoal"])))
            except (KeyError, ValueError):
                continue
        table = build_table(matches)
        if table:
            data[label] = table
            logger.info(f"  ✓ {label}: {len(table)} teams  champion: {min(table, key=table.get)}")
        else:
            logger.warning(f"  ✗ {label}: no data")
            failed.append(label)

    return data, failed


def apply_corrections(data: dict[str, dict[str, int]]) -> None:
    for season, overrides in CORRECTIONS.items():
        if season in data:
            for team, pos in overrides.items():
                data[season][team] = pos


def validate(merged: dict[str, dict[str, int]]) -> list[str]:
    """Return a list of validation errors; empty list = all seasons valid."""
    errors = []
    for s, table in merged.items():
        positions = sorted(table.values())
        expected  = list(range(1, len(table) + 1))
        if positions != expected:
            errors.append(f"{s}: positions {positions[:5]}... (expected 1–{len(table)})")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--refresh", action="store_true",
                        help="Ignore cache and re-fetch every URL")
    args = parser.parse_args()

    os.makedirs("data", exist_ok=True)
    use_cache = not args.refresh
    if args.refresh:
        logger.info("--refresh: ignoring cache")

    primary, primary_failed     = fetch_primary(use_cache)
    apply_corrections(primary)
    secondary, secondary_failed = fetch_secondary(use_cache)

    merged: dict[str, dict[str, int]] = {}
    for label in ["1991/92 (First Div.)", "1992/93"]:
        if label in secondary:
            merged[label] = secondary[label]
    for season in sorted(primary):
        merged[season] = primary[season]

    logger.info("")
    logger.info("=" * 62)
    logger.info("VALIDATION")
    logger.info("=" * 62)
    val_errors = validate(merged)
    if val_errors:
        for e in val_errors:
            logger.error(f"  ✗ {e}")
    else:
        logger.info(f"  ✓ All {len(merged)} seasons pass — positions 1..N complete")

    out = "data/standings_verified.json"
    with open(out, "w") as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)
    logger.info(f"\n✓ Saved {len(merged)} seasons → {out}")

    all_failed = primary_failed + secondary_failed
    if all_failed or val_errors:
        logger.error(f"FAILURES: {len(all_failed)} fetch, {len(val_errors)} validation")
        sys.exit(1)


if __name__ == "__main__":
    main()

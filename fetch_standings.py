#!/usr/bin/env python3
"""Build verified EPL standings from two authoritative sources.

PRIMARY SOURCE (1993/94 – present):
  football-data.co.uk — Joseph Buchdahl's match results database.
  Single consistent schema. Free, no auth required. Industry standard.
  URL: https://www.football-data.co.uk/mmz4281/{YYYY}/E0.csv

SECONDARY SOURCE (1991/92 First Division + 1992/93 inaugural EPL only):
  jalapic/engsoccerdata — R package, English football results since 1888.
  Used solely to fill the two seasons football-data.co.uk doesn't cover.
  URL: https://raw.githubusercontent.com/jalapic/engsoccerdata/master/data-raw/england.csv

Both sources provide match results. Final tables are derived identically from
both using: points → goal difference → goals scored as tiebreakers.

No hardcoding. No API keys required.

Usage:
    python fetch_standings.py
    python generate.py          # auto-detects data/standings_verified.json
"""
import csv
import io
import json
import logging
import os
import urllib.request
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def fetch(url: str) -> str:
    """Fetch URL content as decoded text.

    Args:
        url: The URL to fetch.

    Returns:
        Response body decoded as UTF-8.

    Raises:
        urllib.error.URLError: If the request fails or times out.
    """
    req = urllib.request.Request(url, headers={"User-Agent": "EPL-standings-fetcher/1.0"})
    with urllib.request.urlopen(req, timeout=20) as response:
        return response.read().decode("utf-8", errors="replace")

def build_table(
    matches: list[tuple[str, str, int, int]],
) -> dict[str, int] | None:
    """Derive final league standings from raw match results.

    Applies points → goal difference → goals scored tiebreakers,
    with alphabetical ordering as a final tiebreaker.

    Args:
        matches: List of (home, away, home_goals, away_goals) tuples.

    Returns:
        Dict mapping team name to finishing position (1-indexed),
        or None if no valid matches were provided.
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

    ranked = sorted(
        pts.keys(),
        key=lambda t: (-pts[t], -(gf[t] - ga[t]), -gf[t], t)
    )
    return {team: pos + 1 for pos, team in enumerate(ranked)}

# ── Name normaliser ───────────────────────────────────────────────────────────
# football-data.co.uk uses short names; we normalise to our standard names.
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
    "Blackpool":       "Blackpool",
    "Birmingham":      "Birmingham City",
    "Portsmouth":      "Portsmouth",
    "Norwich":         "Norwich City",
    "Sunderland":      "Sunderland",
    "Brentford":       "Brentford",
    "Luton":           "Luton Town",
    "Barnsley":        "Barnsley",
}

def norm(name: str) -> str:
    """Normalise a team name to its canonical form.

    Maps football-data.co.uk short names (e.g. 'Man United') to the
    canonical names used throughout the project.

    Args:
        name: Raw team name from the data source.

    Returns:
        Canonical team name, or the input unchanged if not in NAMES.
    """
    return NAMES.get(name.strip(), name.strip())



def main() -> None:
    os.makedirs("data", exist_ok=True)

    # ══════════════════════════════════════════════════════════════════════════════
    # PRIMARY SOURCE: football-data.co.uk  (1993/94 – 2025/26)
    # ══════════════════════════════════════════════════════════════════════════════
    logger.info("=" * 62)
    logger.info("PRIMARY: football-data.co.uk  (1993/94 – 2025/26)")
    logger.info("=" * 62)

    BASE = "https://www.football-data.co.uk/mmz4281"

    def season_code(year: int) -> str:
        """Convert a start year to football-data.co.uk season code format.

        Args:
            year: The starting year of the season (e.g. 1993 for 1993/94).

        Returns:
            Two-digit year pair string (e.g. '9394', '1718', '2425').
        """
        return f"{str(year)[2:]}{str(year + 1)[2:]}"

    primary_data = {}
    ERRORS = []

    for year in range(1993, 2026):
        season = f"{year}/{str(year+1)[2:]}"
        url = f"{BASE}/{season_code(year)}/E0.csv"
        try:
            raw = fetch(url)
            reader = csv.DictReader(io.StringIO(raw))
            matches = []
            for row in reader:
                try:
                    home = norm(row["HomeTeam"])
                    away = norm(row["AwayTeam"])
                    hg   = int(row["FTHG"])
                    ag   = int(row["FTAG"])
                    matches.append((home, away, hg, ag))
                except (KeyError, ValueError):
                    continue  # skip incomplete rows (e.g. unplayed fixtures)

            table = build_table(matches)
            if not table:
                logger.info(f"  ✗ {season}: no valid matches")
                continue

            primary_data[season] = table
            champ = min(table, key=table.get)
            n = len(table)
            logger.info(f"  ✓ {season}: {n} teams  champion: {champ}")

        except Exception as e:
            logger.info(f"  ✗ {season}: {e}")
            ERRORS.append(season)

    # ══════════════════════════════════════════════════════════════════════════════
    # SECONDARY SOURCE: jalapic/engsoccerdata (1991/92 + 1992/93 only)
    # ══════════════════════════════════════════════════════════════════════════════
    logger.info("")
    logger.info("=" * 62)
    logger.info("SECONDARY: jalapic/engsoccerdata  (1991/92 + 1992/93 only)")
    logger.info("Reason: football-data.co.uk begins at 1993/94")
    logger.info("=" * 62)

    JALAPIC = ("https://raw.githubusercontent.com/jalapic/engsoccerdata"
               "/master/data-raw/england.csv")

    try:
        raw = fetch(JALAPIC)
        all_rows = list(csv.DictReader(io.StringIO(raw)))
        logger.info(f"  Downloaded {len(all_rows)} match records")

        secondary_data = {}
        for year, label in [(1991, "1991/92 (First Div.)"), (1992, "1992/93")]:
            rows = [r for r in all_rows
                    if r.get("Season") == str(year) and r.get("tier","") == "1"]
            matches = []
            for row in rows:
                try:
                    home = norm(row["home"])
                    away = norm(row["visitor"])
                    hg   = int(row["hgoal"])
                    ag   = int(row["vgoal"])
                    matches.append((home, away, hg, ag))
                except (KeyError, ValueError):
                    continue
            table = build_table(matches)
            if table:
                secondary_data[label] = table
                champ = min(table, key=table.get)
                logger.info(f"  ✓ {label}: {len(table)} teams  champion: {champ}")
            else:
                logger.info(f"  ✗ {label}: no data")

    except Exception as e:
        logger.info(f"  ✗ jalapic fetch failed: {e}")
        secondary_data = {}

    # ══════════════════════════════════════════════════════════════════════════════
    # MERGE: secondary first, then primary (primary wins on any overlap)
    # ══════════════════════════════════════════════════════════════════════════════
    logger.info("")
    logger.info("=" * 62)
    logger.info("VALIDATION")
    logger.info("=" * 62)

    merged = {}
    # Season order: pre-EPL first, then EPL chronologically
    if "1991/92 (First Div.)" in secondary_data:
        merged["1991/92 (First Div.)"] = secondary_data["1991/92 (First Div.)"]
    if "1992/93" in secondary_data:
        merged["1992/93"] = secondary_data["1992/93"]
    for season in sorted(primary_data.keys()):
        merged[season] = primary_data[season]

    # Validate every season
    val_errors = []
    for s, table in merged.items():
        n = len(table)
        positions = sorted(table.values())
        expected  = list(range(1, n + 1))
        if positions != expected:
            val_errors.append(f"  ✗ {s}: positions {positions[:5]}... (expected 1–{n})")

    if val_errors:
        logger.info(f"Validation FAILED — {len(val_errors)} errors:")
        for e in val_errors: logger.info(e)
    else:
        logger.info(f"  ✓ All {len(merged)} seasons pass — positions 1..N complete")

    # Summary
    logger.info("")
    logger.info("Sources:")
    logger.info(f"  jalapic (secondary):          {len(secondary_data)} seasons  "
          f"[{', '.join(secondary_data.keys())}]")
    logger.info(f"  football-data.co.uk (primary): {len(primary_data)} seasons  "
          f"[{min(primary_data)} → {max(primary_data)}]")
    if ERRORS:
        logger.info(f"  Failed to fetch: {ERRORS}")

    # Save
    OUT = "data/standings_verified.json"
    with open(OUT, "w") as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)

    logger.info(f"\n✓ Saved {len(merged)} seasons → {OUT}")
    logger.info("Run: python generate.py")


if __name__ == "__main__":
    main()

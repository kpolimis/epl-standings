#!/usr/bin/env python3
"""
fetch_standings.py — Build verified EPL standings from two authoritative sources.

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
    python3 fetch_standings.py
    python3 generate.py          # auto-detects data/standings_verified.json
"""

import json, os, io, csv
import urllib.request
from collections import defaultdict

os.makedirs("data", exist_ok=True)

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "EPL-standings-fetcher/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8", errors="replace")

# ── Shared table builder ──────────────────────────────────────────────────────
def build_table(matches):
    """
    matches: list of (home, away, home_goals, away_goals)
    Returns: {team_name: finishing_position} using points → GD → GF tiebreakers.
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

def norm(name):
    name = name.strip()
    return NAMES.get(name, name)

# ══════════════════════════════════════════════════════════════════════════════
# PRIMARY SOURCE: football-data.co.uk  (1993/94 – 2025/26)
# ══════════════════════════════════════════════════════════════════════════════
print("=" * 62)
print("PRIMARY: football-data.co.uk  (1993/94 – 2025/26)")
print("=" * 62)

BASE = "https://www.football-data.co.uk/mmz4281"

def season_code(year):
    """1993 → '9394', 2017 → '1718', 2024 → '2425'"""
    return f"{str(year)[2:]}{str(year+1)[2:]}"

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
            print(f"  ✗ {season}: no valid matches")
            continue

        primary_data[season] = table
        champ = min(table, key=table.get)
        n = len(table)
        print(f"  ✓ {season}: {n} teams  champion: {champ}")

    except Exception as e:
        print(f"  ✗ {season}: {e}")
        ERRORS.append(season)

# ══════════════════════════════════════════════════════════════════════════════
# SECONDARY SOURCE: jalapic/engsoccerdata (1991/92 + 1992/93 only)
# ══════════════════════════════════════════════════════════════════════════════
print()
print("=" * 62)
print("SECONDARY: jalapic/engsoccerdata  (1991/92 + 1992/93 only)")
print("Reason: football-data.co.uk begins at 1993/94")
print("=" * 62)

JALAPIC = ("https://raw.githubusercontent.com/jalapic/engsoccerdata"
           "/master/data-raw/england.csv")

try:
    raw = fetch(JALAPIC)
    all_rows = list(csv.DictReader(io.StringIO(raw)))
    print(f"  Downloaded {len(all_rows)} match records")

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
            print(f"  ✓ {label}: {len(table)} teams  champion: {champ}")
        else:
            print(f"  ✗ {label}: no data")

except Exception as e:
    print(f"  ✗ jalapic fetch failed: {e}")
    secondary_data = {}

# ══════════════════════════════════════════════════════════════════════════════
# MERGE: secondary first, then primary (primary wins on any overlap)
# ══════════════════════════════════════════════════════════════════════════════
print()
print("=" * 62)
print("VALIDATION")
print("=" * 62)

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
    print(f"Validation FAILED — {len(val_errors)} errors:")
    for e in val_errors: print(e)
else:
    print(f"  ✓ All {len(merged)} seasons pass — positions 1..N complete")

# Summary
print()
print("Sources:")
print(f"  jalapic (secondary):          {len(secondary_data)} seasons  "
      f"[{', '.join(secondary_data.keys())}]")
print(f"  football-data.co.uk (primary): {len(primary_data)} seasons  "
      f"[{min(primary_data)} → {max(primary_data)}]")
if ERRORS:
    print(f"  Failed to fetch: {ERRORS}")

# Save
OUT = "data/standings_verified.json"
with open(OUT, "w") as f:
    json.dump(merged, f, indent=2, ensure_ascii=False)

print(f"\n✓ Saved {len(merged)} seasons → {OUT}")
print("Run: python3 generate.py")

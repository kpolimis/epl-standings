"""EPL League Positions — Animated Chart Generator.

Run: python generate.py  →  index.html

Requires data/standings_verified.json — run fetch_standings.py first.
"""
import json
import logging
import os
import sys

from html_template import build_html
from team_config import DEFAULT_COLOR, get_initials, meta

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

_VERIFIED_PATH = "data/standings_verified.json"
if not os.path.exists(_VERIFIED_PATH):
    logger.error(f"{_VERIFIED_PATH} not found.")
    logger.error("Run: python fetch_standings.py  to fetch verified data first.")
    sys.exit(1)

with open(_VERIFIED_PATH) as _f:
    _verified = json.load(_f)

_pre  = [s for s in _verified if "First Div" in s]
_epl  = sorted(s for s in _verified if "First Div" not in s)
RAW_DATA = {s: _verified[s] for s in _pre + _epl}
SEASONS  = list(RAW_DATA.keys())
logger.info(f"Loaded {len(SEASONS)} seasons from {_VERIFIED_PATH}")


def main() -> None:
    all_teams = sorted(set().union(*[d.keys() for d in RAW_DATA.values()]))

    teams_js = {
        team: {
            "color":      meta(team).get("color", DEFAULT_COLOR),
            "logo":       meta(team).get("logo", ""),
            "wiki":       meta(team).get("wiki", ""),
            "hl":         meta(team).get("highlight", False),
            "lightBadge": meta(team).get("light_badge", False),
            "initials":   get_initials(team),
            "pos":        [RAW_DATA[s].get(team, None) for s in SEASONS],
        }
        for team in all_teams
    }

    payload = {"seasons": SEASONS, "teams": teams_js, "raw": RAW_DATA}
    js_data = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(build_html(js_data, SEASONS))
    logger.info("✓ index.html")

    os.makedirs("data", exist_ok=True)
    standings = {
        "seasons": SEASONS,
        "raw":     RAW_DATA,
        "teams":   {t: {"pos": v["pos"], "initials": v["initials"]}
                    for t, v in teams_js.items()},
    }
    with open("data/standings.json", "w", encoding="utf-8") as f:
        json.dump(standings, f, ensure_ascii=False, indent=2)
    logger.info("✓ data/standings.json")


if __name__ == "__main__":
    main()

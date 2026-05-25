"""Spot-check verified standings against historical facts.

These tests guard against silent regressions in the data pipeline —
specifically the kinds of bugs we hit before (hardcoded 1991/92 errors,
1996/97 Middlesbrough points deduction).

Run: pytest tests/test_standings.py
"""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

STANDINGS_PATH = "data/standings_verified.json"


@pytest.fixture(scope="module")
def standings():
    with open(STANDINGS_PATH) as f:
        return json.load(f)


def test_positions_are_contiguous(standings):
    """Every season's positions must be exactly 1..N with no gaps or duplicates."""
    for season, table in standings.items():
        positions = sorted(table.values())
        expected  = list(range(1, len(table) + 1))
        assert positions == expected, f"{season}: {positions} != {expected}"


def test_1991_92_norwich_at_18(standings):
    """1991/92: Norwich City was 18th in the final First Division season."""
    table = standings["1991/92 (First Div.)"]
    assert table["Norwich City"] == 18


def test_1991_92_ipswich_not_present(standings):
    """1991/92: Ipswich Town was in Division 2, not First Division."""
    assert "Ipswich Town" not in standings["1991/92 (First Div.)"]


def test_1991_92_leeds_champion(standings):
    """1991/92: Leeds United won the final First Division title."""
    assert standings["1991/92 (First Div.)"]["Leeds United"] == 1


def test_1992_93_man_utd_inaugural_champion(standings):
    """1992/93: Manchester United won the inaugural Premier League."""
    assert standings["1992/93"]["Manchester United"] == 1


def test_1996_97_middlesbrough_relegated(standings):
    """1996/97: Middlesbrough finished 19th and were relegated.

    Their match-derived position would have been ~14th, but they were
    deducted 3 points for failing to fulfil a fixture at Blackburn.
    """
    assert standings["1996/97"]["Middlesbrough"] == 19


def test_1996_97_no_gaps_after_correction(standings):
    """Applying the Middlesbrough correction must not leave duplicate positions."""
    table = standings["1996/97"]
    assert len(set(table.values())) == len(table)


def test_2003_04_arsenal_invincibles(standings):
    """2003/04: Arsenal's Invincibles won the league unbeaten."""
    assert standings["2003/04"]["Arsenal"] == 1


def test_2015_16_leicester_champions(standings):
    """2015/16: Leicester City's 5000-1 title."""
    assert standings["2015/16"]["Leicester City"] == 1


def test_every_epl_season_has_20_or_22_teams(standings):
    """EPL seasons had 22 teams (1992-1995) or 20 teams (1995-present)."""
    for season, table in standings.items():
        if "First Div" in season:
            continue
        assert len(table) in (20, 22), f"{season} has {len(table)} teams"


def test_qpr_normalisation(standings):
    """QPR must be normalised to 'QPR', never 'Queens Park Rangers'."""
    for season, table in standings.items():
        assert "Queens Park Rangers" not in table, f"{season} has un-normalised QPR"

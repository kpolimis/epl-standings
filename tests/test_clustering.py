"""Sanity tests for the shared clustering module."""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from clustering import (
    FEATURE_COLS, assign_labels, compute_cluster_stats,
    extract_features, fit_clusters,
)


def test_extract_features_empty_returns_none():
    assert extract_features([None, None, None]) is None


def test_extract_features_single_stint():
    # 3 consecutive seasons then gone
    feats = extract_features([1, 2, 3, None, None])
    assert feats["n_seasons"] == 3
    assert feats["first_season"] == 0
    assert feats["currently_in"] == 0
    assert feats["stints"] == 1
    assert feats["max_consecutive_run"] == 3
    assert feats["best_position"] == 1
    assert feats["avg_position"] == 2.0


def test_extract_features_multi_stint():
    # Seasons 0,1 then gap then 3,4 then gap then 6
    feats = extract_features([5, 10, None, 8, 12, None, 15])
    assert feats["n_seasons"] == 5
    assert feats["stints"] == 3
    assert feats["max_consecutive_run"] == 2
    assert feats["currently_in"] == 1
    assert feats["best_position"] == 5


def test_extract_features_returns_all_required_columns():
    feats = extract_features([1, 2, 3])
    for col in FEATURE_COLS:
        assert col in feats, f"missing feature {col}"


def test_fit_clusters_assigns_one_label_per_row():
    rows = [extract_features([1] * i + [None] * (20 - i)) for i in range(2, 22)]
    labels = fit_clusters(rows, n_clusters=3, seed=42)
    assert len(labels) == len(rows)
    assert set(labels).issubset({0, 1, 2})


def test_fit_clusters_is_deterministic():
    rows = [extract_features([1] * i + [None] * (20 - i)) for i in range(2, 22)]
    a = fit_clusters(rows, seed=42)
    b = fit_clusters(rows, seed=42)
    assert list(a) == list(b)


def test_assign_labels_always_returns_four_distinct():
    """Even with degenerate stats the four labels must all appear."""
    stats = {
        0: {"avg_seasons": 30, "pct_current": 0.9, "avg_stints": 1.0, "avg_first": 0,  "avg_max_run": 30, "avg_position": 6,  "best_position": 1,  "n": 5, "members": []},
        1: {"avg_seasons": 5,  "pct_current": 0.4, "avg_stints": 2.5, "avg_first": 10, "avg_max_run": 3,  "avg_position": 16, "best_position": 12, "n": 8, "members": []},
        2: {"avg_seasons": 3,  "pct_current": 0.8, "avg_stints": 1.0, "avg_first": 28, "avg_max_run": 3,  "avg_position": 13, "best_position": 8,  "n": 4, "members": []},
        3: {"avg_seasons": 4,  "pct_current": 0.0, "avg_stints": 1.2, "avg_first": 5,  "avg_max_run": 4,  "avg_position": 17, "best_position": 13, "n": 6, "members": []},
    }
    labels = assign_labels(stats)
    label_names = {tup[0] for tup in labels.values()}
    assert label_names == {"Permanent fixtures", "Yo-yo regulars",
                           "Modern era entrants", "EPL tourists"}

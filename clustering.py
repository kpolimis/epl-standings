"""Shared feature extraction, clustering, and labeling for EPL trajectories.

Single source of truth for:
  - The feature set used to cluster clubs
  - The KMeans configuration (k, seed, scaler)
  - Cluster label assignment (rank-based, not threshold-based)

Both cluster_trajectories.py (stdout report) and generate_trajectories.py
(HTML output) import from this module so their results cannot disagree.
"""
from __future__ import annotations

import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

N_CLUSTERS: int = 4
RANDOM_SEED: int = 42

# Feature set: 7 features, no high-collinearity pairs.
# `last_season` was dropped — strongly correlated with `currently_in`
# (last_season == N-1 ⇔ currently_in == 1).
FEATURE_COLS: list[str] = [
    "n_seasons",            # how many top-flight seasons total
    "first_season",         # season index of first appearance
    "currently_in",         # 1 if present in latest season else 0
    "stints",               # number of separate spells in the top flight
    "max_consecutive_run",  # longest unbroken streak
    "avg_position",         # mean league position when present
    "best_position",        # lowest-numbered (best) finish ever
]


def extract_features(pos: list[int | None]) -> dict[str, float] | None:
    """Extract clustering features from a club's season-by-season positions.

    Args:
        pos: League position per season; None when the club was not top-flight.

    Returns:
        Dict of feature name to value, or None if the club has zero appearances.
    """
    present = [i for i, p in enumerate(pos) if p is not None]
    if not present:
        return None

    stints = 1
    for i in range(1, len(present)):
        if present[i] != present[i - 1] + 1:
            stints += 1

    max_run = run = 1
    for i in range(1, len(present)):
        run = run + 1 if present[i] == present[i - 1] + 1 else 1
        max_run = max(max_run, run)

    positions = [p for p in pos if p is not None]

    return {
        "n_seasons":           len(present),
        "first_season":        float(present[0]),
        "currently_in":        1.0 if pos[-1] is not None else 0.0,
        "stints":              float(stints),
        "max_consecutive_run": float(max_run),
        "avg_position":        float(np.mean(positions)),
        "best_position":       float(min(positions)),
    }


def fit_clusters(
    feature_rows: list[dict[str, float]],
    n_clusters: int = N_CLUSTERS,
    seed: int = RANDOM_SEED,
) -> np.ndarray:
    """Standardise features and fit KMeans, returning a label per row."""
    X = np.array([[row[col] for col in FEATURE_COLS] for row in feature_rows])
    X_scaled = StandardScaler().fit_transform(X)
    np.random.seed(seed)
    km = KMeans(n_clusters=n_clusters, n_init=20, random_state=seed)
    return km.fit_predict(X_scaled)


def compute_cluster_stats(
    records: list[dict],
    n_clusters: int = N_CLUSTERS,
) -> dict[int, dict]:
    """Aggregate per-cluster summary statistics from labeled feature records."""
    stats = {}
    for c_id in range(n_clusters):
        members = [r for r in records if r["cluster"] == c_id]
        if not members:
            continue
        stats[c_id] = {
            "n":            len(members),
            "avg_seasons":  float(np.mean([r["n_seasons"] for r in members])),
            "avg_first":    float(np.mean([r["first_season"] for r in members])),
            "pct_current":  float(np.mean([r["currently_in"] for r in members])),
            "avg_stints":   float(np.mean([r["stints"] for r in members])),
            "avg_max_run":  float(np.mean([r["max_consecutive_run"] for r in members])),
            "avg_position": float(np.mean([r["avg_position"] for r in members])),
            "best_position":float(np.mean([r["best_position"] for r in members])),
            "members":      sorted(r["team"] for r in members),
        }
    return stats


def assign_labels(stats: dict[int, dict]) -> dict[int, tuple[str, str, str]]:
    """Assign (label, color, description) per cluster by rank, not threshold.

    Why rank-based: threshold rules like ``avg_seasons > 25 and pct_current > 0.8``
    silently break on re-runs with one more season of data. Sorting clusters by
    interpretable axes (stability, recency, volatility) always yields four
    distinct labels regardless of the underlying values.

    Returns:
        cluster_id → (label, hex_color, description) for HTML + stdout reuse.
    """
    LABELS = ["Permanent fixtures", "Yo-yo regulars",
              "Modern era entrants", "EPL tourists"]
    COLORS = ["#F59E0B", "#3B82F6", "#8B5CF6", "#6B7280"]
    DESCS  = ["Present every season, or close to it",
              "Multiple stints — half still in the league, half not",
              "Single-stint mid-table clubs; most are now gone",
              "Played their seasons and are now gone"]

    remaining = set(stats.keys())
    ordered: list[int] = []

    # 1. Most stable: highest avg_seasons × pct_current
    perm = max(remaining, key=lambda c: stats[c]["avg_seasons"] * stats[c]["pct_current"])
    ordered.append(perm); remaining.remove(perm)

    # 2. Yo-yo: highest stints among the rest
    yoyo = max(remaining, key=lambda c: stats[c]["avg_stints"])
    ordered.append(yoyo); remaining.remove(yoyo)

    # 3. Modern entrants: latest first_season among the rest
    modern = max(remaining, key=lambda c: stats[c]["avg_first"])
    ordered.append(modern); remaining.remove(modern)

    # 4. Whatever's left → tourists
    ordered.extend(remaining)

    return {c_id: (LABELS[i], COLORS[i], DESCS[i]) for i, c_id in enumerate(ordered)}

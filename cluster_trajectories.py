"""Standalone k-means cluster analysis of EPL club trajectories.

Prints a cluster summary and club-level table to stdout.
Run: python cluster_trajectories.py
Reads: data/standings.json (produced by generate.py)
"""
import json
import logging

import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

N_CLUSTERS: int = 4
RANDOM_SEED: int = 42
FEATURE_COLS: list[str] = [
    "n_seasons", "first_season", "last_season",
    "currently_in", "stints", "max_consecutive_run",
]


def extract_features(pos: list[int | None]) -> dict[str, int | float] | None:
    """Extract scalar clustering features from a club's position history.

    Args:
        pos: Season-by-season league positions; None when not in the EPL.

    Returns:
        Dict mapping feature name to value, or None if the club has no
        top-flight appearances.
    """
    present = [idx for idx, p in enumerate(pos) if p is not None]
    if not present:
        return None

    n_seasons = len(present)
    first_season = present[0]
    last_season = present[-1]
    currently_in = 1 if pos[-1] is not None else 0

    stints = 1
    for i in range(1, len(present)):
        if present[i] != present[i - 1] + 1:
            stints += 1

    max_run = 1
    run = 1
    for i in range(1, len(present)):
        if present[i] == present[i - 1] + 1:
            run += 1
            max_run = max(max_run, run)
        else:
            run = 1

    avg_pos = float(np.mean([p for p in pos if p is not None]))

    return {
        "n_seasons": n_seasons,
        "first_season": first_season,
        "last_season": last_season,
        "currently_in": currently_in,
        "stints": stints,
        "max_consecutive_run": max_run,
        "avg_position": avg_pos,
    }


def label_cluster(stats: dict[str, float]) -> str:
    """Assign a human-readable label to a cluster based on aggregate statistics.

    Args:
        stats: Cluster summary containing avg_seasons, pct_current,
               avg_first, and avg_stints.

    Returns:
        Descriptive label string for the cluster.
    """
    if stats["avg_seasons"] > 25 and stats["pct_current"] > 0.8:
        return "Permanent fixtures"
    if stats["avg_first"] > 15 and stats["pct_current"] > 0.8:
        return "Late arrivals who stayed"
    if stats["avg_stints"] > 1.5 and stats["pct_current"] < 0.5:
        return "Yo-yo clubs (mostly gone)"
    if stats["avg_stints"] > 1.3:
        return "Yo-yo clubs (some still present)"
    if stats["pct_current"] < 0.3 and stats["avg_seasons"] < 10:
        return "EPL tourists"
    return "Mid-tenure clubs"


def main() -> None:
    with open("data/standings.json") as f:
        data = json.load(f)

    seasons: list[str] = data["seasons"]
    teams: dict = data["teams"]
    n_seasons: int = len(seasons)

    records: list[dict] = []
    for team_name, team_data in teams.items():
        features = extract_features(team_data["pos"])
        if features:
            features["team"] = team_name
            records.append(features)

    X = np.array([[record[col] for col in FEATURE_COLS] for record in records])

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    np.random.seed(RANDOM_SEED)
    km = KMeans(n_clusters=N_CLUSTERS, n_init=20, random_state=RANDOM_SEED)
    labels = km.fit_predict(X_scaled)

    for idx, record in enumerate(records):
        record["cluster"] = int(labels[idx])

    cluster_stats: dict[int, dict] = {}
    for cluster_id in range(N_CLUSTERS):
        members = [r for r in records if r["cluster"] == cluster_id]
        cluster_stats[cluster_id] = {
            "n": len(members),
            "avg_seasons": np.mean([r["n_seasons"] for r in members]),
            "avg_first": np.mean([r["first_season"] for r in members]),
            "avg_last": np.mean([r["last_season"] for r in members]),
            "pct_current": np.mean([r["currently_in"] for r in members]),
            "avg_stints": np.mean([r["stints"] for r in members]),
            "avg_max_run": np.mean([r["max_consecutive_run"] for r in members]),
            "members": sorted([r["team"] for r in members]),
        }

    for cluster_id, stats in cluster_stats.items():
        stats["label"] = label_cluster(stats)

    logger.info("=" * 60)
    logger.info("EPL CLUB TRAJECTORY CLUSTERS")
    logger.info("=" * 60)

    for cluster_id in sorted(cluster_stats, key=lambda x: -cluster_stats[x]["avg_seasons"]):
        stats = cluster_stats[cluster_id]
        logger.info("\nCluster %d: %s (n=%d)", cluster_id, stats["label"], stats["n"])
        logger.info("  Avg seasons in EPL:   %.1f", stats["avg_seasons"])
        avg_first_idx = int(stats["avg_first"])
        season_label = seasons[avg_first_idx] if avg_first_idx < n_seasons else "N/A"
        logger.info("  Avg first season idx: %.1f  (%s)", stats["avg_first"], season_label)
        logger.info("  Currently in league:  %.0f%%", stats["pct_current"] * 100)
        logger.info("  Avg stints:           %.2f", stats["avg_stints"])
        logger.info("  Avg longest run:      %.1f seasons", stats["avg_max_run"])
        logger.info("  Teams: %s", ", ".join(stats["members"]))

    logger.info("\n\n" + "=" * 60)
    logger.info("CLUB-LEVEL TABLE (for blog)")
    logger.info("=" * 60)
    logger.info("%-28s %7s %6s %7s  %s", "Team", "Seasons", "Stints", "Current", "Cluster Label")
    logger.info("-" * 70)
    for record in sorted(records, key=lambda x: (-x["n_seasons"], x["team"])):
        cluster_id = record["cluster"]
        cluster_label = cluster_stats[cluster_id]["label"]
        current = "yes" if record["currently_in"] else "no"
        logger.info("%-28s %7d %6d %7s  %s",
                    record["team"], record["n_seasons"], record["stints"],
                    current, cluster_label)


if __name__ == "__main__":
    main()

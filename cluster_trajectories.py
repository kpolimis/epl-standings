"""Standalone k-means cluster analysis of EPL club trajectories.

Prints a cluster summary and club-level table to stdout.
Run: python cluster_trajectories.py
Reads: data/standings.json (produced by generate.py)
"""
import json
import logging

from clustering import (
    N_CLUSTERS, assign_labels, compute_cluster_stats,
    extract_features, fit_clusters,
)

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


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

    labels = fit_clusters(records)
    for idx, record in enumerate(records):
        record["cluster"] = int(labels[idx])

    cluster_stats = compute_cluster_stats(records)
    cluster_labels = assign_labels(cluster_stats)
    for c_id, (label, _color, _desc) in cluster_labels.items():
        cluster_stats[c_id]["label"] = label

    logger.info("=" * 60)
    logger.info("EPL CLUB TRAJECTORY CLUSTERS")
    logger.info("=" * 60)

    for c_id in sorted(cluster_stats, key=lambda x: -cluster_stats[x]["avg_seasons"]):
        s = cluster_stats[c_id]
        avg_first_idx = int(s["avg_first"])
        season_label = seasons[avg_first_idx] if avg_first_idx < n_seasons else "N/A"
        logger.info("\nCluster %d: %s (n=%d)", c_id, s["label"], s["n"])
        logger.info("  Avg seasons in EPL:   %.1f", s["avg_seasons"])
        logger.info("  Avg first season idx: %.1f  (%s)", s["avg_first"], season_label)
        logger.info("  Currently in league:  %.0f%%", s["pct_current"] * 100)
        logger.info("  Avg stints:           %.2f", s["avg_stints"])
        logger.info("  Avg longest run:      %.1f seasons", s["avg_max_run"])
        logger.info("  Avg position:         %.1f", s["avg_position"])
        logger.info("  Avg best finish:      %.1f", s["best_position"])
        logger.info("  Teams: %s", ", ".join(s["members"]))

    logger.info("\n\n" + "=" * 60)
    logger.info("CLUB-LEVEL TABLE (for blog)")
    logger.info("=" * 60)
    logger.info("%-28s %7s %6s %7s  %s", "Team", "Seasons", "Stints", "Current", "Cluster Label")
    logger.info("-" * 70)
    for r in sorted(records, key=lambda x: (-x["n_seasons"], x["team"])):
        current = "yes" if r["currently_in"] else "no"
        logger.info("%-28s %7d %6d %7s  %s",
                    r["team"], int(r["n_seasons"]), int(r["stints"]),
                    current, cluster_stats[r["cluster"]]["label"])


if __name__ == "__main__":
    main()

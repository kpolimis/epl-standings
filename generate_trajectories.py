"""Generate trajectories.html — k-means cluster visualization of EPL clubs.

Reads:    data/standings.json (produced by generate.py)
Writes:   trajectories.html
"""
import json
import logging

from clustering import assign_labels, compute_cluster_stats, extract_features, fit_clusters
from trajectories_template import build_html

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    with open("data/standings.json") as f:
        data = json.load(f)

    seasons: list[str] = data["seasons"]
    teams: dict = data["teams"]

    records: list[dict] = []
    for name, team_data in teams.items():
        feats = extract_features(team_data["pos"])
        if feats:
            feats["team"] = name
            records.append(feats)

    labels = fit_clusters(records)
    for idx, r in enumerate(records):
        r["cluster"] = int(labels[idx])

    cluster_stats = compute_cluster_stats(records)
    cluster_labels = assign_labels(cluster_stats)

    payload_clusters = []
    for c_id, (label, color, desc) in cluster_labels.items():
        members = sorted(
            [r for r in records if r["cluster"] == c_id],
            key=lambda r: -r["n_seasons"],
        )
        payload_clusters.append({
            "label": label,
            "color": color,
            "desc":  desc,
            "n":     len(members),
            "teams": [
                {
                    "name":         r["team"],
                    "pos":          teams[r["team"]]["pos"],
                    "n_seasons":    int(r["n_seasons"]),
                    "stints":       int(r["stints"]),
                    "currently_in": bool(r["currently_in"]),
                }
                for r in members
            ],
        })

    js_data = json.dumps(
        {"seasons": seasons, "clusters": payload_clusters},
        ensure_ascii=False, separators=(",", ":"),
    )
    n_epl = sum(1 for s in seasons if "First Div" not in s)

    with open("trajectories.html", "w", encoding="utf-8") as f:
        f.write(build_html(js_data, n_epl))
    logger.info("✓ trajectories.html")


if __name__ == "__main__":
    main()

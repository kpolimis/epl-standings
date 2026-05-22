import json
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

with open("data/standings.json") as f:
    d = json.load(f)

seasons = d["seasons"]
teams = d["teams"]
N = len(seasons)  # 35


def extract_features(pos):
    present = [i for i, p in enumerate(pos) if p is not None]
    if not present:
        return None

    n_seasons = len(present)
    first_season = present[0]
    last_season = present[-1]
    currently_in = 1 if pos[-1] is not None else 0

    # Count distinct stints (gaps in presence)
    stints = 1
    for i in range(1, len(present)):
        if present[i] != present[i - 1] + 1:
            stints += 1

    # Longest consecutive run
    max_run = 1
    run = 1
    for i in range(1, len(present)):
        if present[i] == present[i - 1] + 1:
            run += 1
            max_run = max(max_run, run)
        else:
            run = 1

    # Avg position when present (lower number = better)
    avg_pos = np.mean([p for p in pos if p is not None])

    return {
        "n_seasons": n_seasons,
        "first_season": first_season,
        "last_season": last_season,
        "currently_in": currently_in,
        "stints": stints,
        "max_consecutive_run": max_run,
        "avg_position": avg_pos,
    }


records = []
for name, t in teams.items():
    feats = extract_features(t["pos"])
    if feats:
        feats["team"] = name
        records.append(feats)

feature_cols = ["n_seasons", "first_season", "last_season", "currently_in", "stints", "max_consecutive_run"]
X = np.array([[r[c] for c in feature_cols] for r in records])

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

np.random.seed(42)
km = KMeans(n_clusters=4, n_init=20, random_state=42)
labels = km.fit_predict(X_scaled)

for i, r in enumerate(records):
    r["cluster"] = int(labels[i])

# Label clusters by their dominant characteristics
cluster_stats = {}
for c in range(4):
    members = [r for r in records if r["cluster"] == c]
    cluster_stats[c] = {
        "n": len(members),
        "avg_seasons": np.mean([r["n_seasons"] for r in members]),
        "avg_first": np.mean([r["first_season"] for r in members]),
        "avg_last": np.mean([r["last_season"] for r in members]),
        "pct_current": np.mean([r["currently_in"] for r in members]),
        "avg_stints": np.mean([r["stints"] for r in members]),
        "avg_max_run": np.mean([r["max_consecutive_run"] for r in members]),
        "members": sorted([r["team"] for r in members]),
    }

# Assign human-readable labels based on cluster characteristics
def label_cluster(stats):
    if stats["avg_seasons"] > 25 and stats["pct_current"] > 0.8:
        return "Permanent fixtures"
    elif stats["avg_first"] > 15 and stats["pct_current"] > 0.8:
        return "Late arrivals who stayed"
    elif stats["avg_stints"] > 1.5 and stats["pct_current"] < 0.5:
        return "Yo-yo clubs (mostly gone)"
    elif stats["avg_stints"] > 1.3:
        return "Yo-yo clubs (some still present)"
    elif stats["pct_current"] < 0.3 and stats["avg_seasons"] < 10:
        return "One-time visitors"
    else:
        return "Mid-tenure clubs"

for c, s in cluster_stats.items():
    s["label"] = label_cluster(s)

print("=" * 60)
print("EPL CLUB TRAJECTORY CLUSTERS")
print("=" * 60)

for c in sorted(cluster_stats, key=lambda x: -cluster_stats[x]["avg_seasons"]):
    s = cluster_stats[c]
    print(f"\nCluster {c}: {s['label']} (n={s['n']})")
    print(f"  Avg seasons in EPL:   {s['avg_seasons']:.1f}")
    print(f"  Avg first season idx: {s['avg_first']:.1f}  ({seasons[int(s['avg_first'])] if int(s['avg_first']) < N else 'N/A'})")
    print(f"  Currently in league:  {s['pct_current']*100:.0f}%")
    print(f"  Avg stints:           {s['avg_stints']:.2f}")
    print(f"  Avg longest run:      {s['avg_max_run']:.1f} seasons")
    print(f"  Teams: {', '.join(s['members'])}")

# Print club-level for blog prose
print("\n\n" + "=" * 60)
print("CLUB-LEVEL TABLE (for blog)")
print("=" * 60)
print(f"{'Team':<28} {'Seasons':>7} {'Stints':>6} {'Current':>7} {'Cluster Label'}")
print("-" * 70)
for r in sorted(records, key=lambda x: (-x["n_seasons"], x["team"])):
    c = r["cluster"]
    label = cluster_stats[c]["label"]
    print(f"{r['team']:<28} {r['n_seasons']:>7} {r['stints']:>6} {'yes' if r['currently_in'] else 'no':>7}  {label}")

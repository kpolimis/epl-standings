"""Justify k=4 with elbow + silhouette analysis.

Writes docs/elbow.png — a two-panel chart of inertia and silhouette
score across k=2..10 — for inclusion in the technical blog post.

Run: python elbow_analysis.py
"""
import json
import logging
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from clustering import FEATURE_COLS, RANDOM_SEED, extract_features

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

K_RANGE = range(2, 11)
OUT_PATH = "docs/elbow.png"


def main() -> None:
    with open("data/standings.json") as f:
        data = json.load(f)

    rows = []
    for name, td in data["teams"].items():
        feats = extract_features(td["pos"])
        if feats:
            rows.append(feats)

    X = np.array([[r[c] for c in FEATURE_COLS] for r in rows])
    X_scaled = StandardScaler().fit_transform(X)

    inertias, silhouettes = [], []
    for k in K_RANGE:
        np.random.seed(RANDOM_SEED)
        km = KMeans(n_clusters=k, n_init=20, random_state=RANDOM_SEED).fit(X_scaled)
        inertias.append(km.inertia_)
        silhouettes.append(silhouette_score(X_scaled, km.labels_))
        logger.info(f"  k={k}: inertia={km.inertia_:.1f}  silhouette={silhouettes[-1]:.3f}")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2), facecolor="#0d1117")
    for ax in (ax1, ax2):
        ax.set_facecolor("#0d1117")
        ax.tick_params(colors="#c9d1d9")
        for spine in ax.spines.values():
            spine.set_color("#30363d")
        ax.grid(color="#21262d", linestyle="-", linewidth=0.5, alpha=0.5)

    ax1.plot(list(K_RANGE), inertias, "o-", color="#58a6ff", lw=2, ms=7)
    ax1.axvline(4, color="#f59e0b", lw=1, ls="--", alpha=0.7)
    ax1.set_xlabel("k (number of clusters)", color="#c9d1d9")
    ax1.set_ylabel("Inertia (within-cluster sum of squares)", color="#c9d1d9")
    ax1.set_title("Elbow plot", color="#f0f4f8", fontsize=13, pad=10)

    ax2.plot(list(K_RANGE), silhouettes, "o-", color="#3fb950", lw=2, ms=7)
    ax2.axvline(4, color="#f59e0b", lw=1, ls="--", alpha=0.7)
    ax2.set_xlabel("k (number of clusters)", color="#c9d1d9")
    ax2.set_ylabel("Silhouette score (higher = better separation)", color="#c9d1d9")
    ax2.set_title("Silhouette scores", color="#f0f4f8", fontsize=13, pad=10)

    fig.suptitle(f"Cluster-count selection (n={len(rows)} clubs, {len(FEATURE_COLS)} features)",
                 color="#f0f4f8", fontsize=14, y=1.02)
    fig.tight_layout()

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    fig.savefig(OUT_PATH, dpi=140, bbox_inches="tight",
                facecolor="#0d1117", edgecolor="none")
    logger.info(f"✓ wrote {OUT_PATH}")


if __name__ == "__main__":
    main()

"""Generate trajectories.html — k-means cluster visualization of EPL clubs.

Clusters 52 clubs into four trajectory types based on presence patterns
across 35 top-flight seasons. Produces a self-contained D3.js sparkline grid.

Run: python generate_trajectories.py  →  trajectories.html
Requires: numpy, scikit-learn
Reads:    data/standings.json (produced by generate.py)
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


def extract_features(pos: list[int | None]) -> list[int | float] | None:
    """Extract scalar clustering features from a club's position history.

    Args:
        pos: Season-by-season league positions; None when not in the EPL.

    Returns:
        Six-element feature vector
        [n_seasons, first_season, last_season, currently_in, stints, max_run],
        or None if the club has no top-flight appearances.
    """
    present = [idx for idx, p in enumerate(pos) if p is not None]
    if not present:
        return None
    n_seasons    = len(present)
    first_season = present[0]
    last_season  = present[-1]
    currently_in = 1 if pos[-1] is not None else 0

    stints = 1
    for i in range(1, len(present)):
        if present[i] != present[i - 1] + 1:
            stints += 1

    run, max_run = 1, 1
    for i in range(1, len(present)):
        run = run + 1 if present[i] == present[i - 1] + 1 else 1
        max_run = max(max_run, run)

    return [n_seasons, first_season, last_season, currently_in, stints, max_run]



def main() -> None:
    # ── Load data ──────────────────────────────────────────────────
    with open("data/standings.json") as f:
        data = json.load(f)

    seasons: list[str] = data["seasons"]
    teams: dict = data["teams"]

    # ── Build features ─────────────────────────────────────────────
    team_names = [t for t in teams if extract_features(teams[t]["pos"]) is not None]
    X = np.array([extract_features(teams[t]["pos"]) for t in team_names])

    # ── Cluster ────────────────────────────────────────────────────
    scaler   = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    np.random.seed(RANDOM_SEED)
    km     = KMeans(n_clusters=N_CLUSTERS, n_init=20, random_state=RANDOM_SEED)
    labels = km.fit_predict(X_scaled)

    raw_clusters: dict[int, list] = {}
    for idx, team_name in enumerate(team_names):
        cluster_id = int(labels[idx])
        if cluster_id not in raw_clusters:
            raw_clusters[cluster_id] = []
        feats = extract_features(teams[team_name]["pos"])
        raw_clusters[cluster_id].append((team_name, feats))
    def cluster_sort_key(cluster_id: int) -> tuple[float, float]:
        """Compute a sort key that places permanent fixtures first.

        Args:
            cluster_id: Integer cluster label from KMeans.

        Returns:
            Tuple (score, avg_first) where lower score = higher priority.
            Permanent fixtures (high seasons, high current, early arrival) sort first.
        """
        members = raw_clusters[cluster_id]
        avg_seasons = np.mean([f[0] for _, f in members])
        pct_current = np.mean([f[3] for _, f in members])
        avg_first   = np.mean([f[1] for _, f in members])
        return (-avg_seasons * pct_current, avg_first)

    sorted_cluster_ids = sorted(raw_clusters.keys(), key=cluster_sort_key)

    LABELS = ["Permanent fixtures", "Yo-yo regulars", "Modern era entrants", "EPL tourists"]
    COLORS = ["#F59E0B", "#3B82F6", "#8B5CF6", "#6B7280"]
    DESCS  = [
        "Present every season, or close to it",
        "Multiple stints — half still in the league, half not",
        "Post-2011 arrivals; most came briefly and left",
        "Played their seasons and are now gone",
    ]

    # ── Build JSON payload for the chart ──────────────────────────
    payload_clusters = []
    for rank, c_id in enumerate(sorted_cluster_ids):
        members = raw_clusters[c_id]
        members.sort(key=lambda x: -x[1][0])  # sort by n_seasons desc
        payload_clusters.append({
            "label":  LABELS[rank],
            "color":  COLORS[rank],
            "desc":   DESCS[rank],
            "n":      len(members),
            "teams":  [
                {
                    "name":         name,
                    "pos":          teams[name]["pos"],
                    "n_seasons":    feats[0],
                    "stints":       feats[4],
                    "currently_in": bool(feats[3]),
                }
                for name, feats in members
            ],
        })

    JS_DATA = json.dumps(
        {"seasons": seasons, "clusters": payload_clusters},
        ensure_ascii=False, separators=(",", ":"),
    )

    # ─────────────────────────────────────────────────────────────────
    HTML = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>EPL Club Trajectories — Four Clusters</title>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@900&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
    *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
    :root{{
      --bg:#07090d;--surface:#0d1117;--border:#21262d;
      --text:#c9d1d9;--muted:#6e7681;
    }}
    body{{
      background:var(--bg);color:var(--text);
      font-family:'IBM Plex Mono',monospace;
      max-width:1200px;margin:0 auto;padding:32px 24px 60px;
    }}
    h1{{
      font-family:'Playfair Display',serif;font-size:clamp(22px,3vw,40px);
      font-weight:900;color:#f0f4f8;letter-spacing:-.02em;margin-bottom:6px;
    }}
    .subtitle{{
      font-size:11px;color:var(--muted);letter-spacing:.09em;
      text-transform:uppercase;margin-bottom:36px;
    }}
    .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(520px,1fr));gap:28px;}}
    .panel{{
      background:var(--surface);border:1px solid var(--border);
      border-radius:10px;padding:20px 22px 24px;
    }}
    .panel-header{{
      display:flex;align-items:baseline;gap:10px;margin-bottom:4px;
      padding-bottom:12px;border-bottom:1px solid var(--border);
    }}
    .panel-title{{
      font-size:14px;font-weight:600;color:#f0f4f8;
    }}
    .panel-count{{font-size:11px;color:var(--muted);}}
    .panel-desc{{font-size:10px;color:var(--muted);margin-bottom:16px;margin-top:4px;letter-spacing:.03em;}}
    .club-row{{
      display:flex;align-items:center;gap:10px;
      padding:3px 0;border-bottom:1px solid #ffffff06;
    }}
    .club-row:last-child{{border-bottom:none;}}
    .club-name{{
      width:180px;flex-shrink:0;font-size:10px;
      color:#c9d1d9;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
    }}
    .club-meta{{
      width:60px;flex-shrink:0;font-size:9px;
      color:var(--muted);text-align:right;
    }}
    .spark-wrap{{flex:1;overflow:hidden;}}
    .spark-wrap svg{{display:block;width:100%;}}
    .season-axis{{
      display:flex;justify-content:space-between;
      font-size:8px;color:#333;margin-top:8px;padding:0 0 0 190px;
    }}
    footer{{
      margin-top:48px;font-size:10px;color:#484f58;
      border-top:1px solid var(--border);padding-top:16px;
      line-height:1.9;
    }}
    footer a{{color:#58a6ff;text-decoration:none;}}
    </style>
    </head>
    <body>
    <h1>Four EPL Club Trajectories</h1>
    <p class="subtitle">k-means clustering · 52 clubs · 34 EPL seasons · 1 First Division (1991/92–2025/26) · 6 features</p>
    <div class="grid" id="grid"></div>
    <footer>
      k-means (k=4) on: seasons played, first appearance, last appearance, currently in league, number of stints, longest consecutive run.<br>
      Position data from official Premier League records. 2025/26 with one matchweek remaining (May 2026).<br>
      <a href="https://github.com/kpolimis/epl-standings" target="_blank">github.com/kpolimis/epl-standings</a>
      · <a href="index.html">← back to full chart</a>
    </footer>
    <script>
    const DATA = {JS_DATA};
    const seasons = DATA.seasons;
    const N = seasons.length;
    const SPARK_W = 300, SPARK_H = 36, PAD = 2;
    const xSc = d3.scalePoint().domain(d3.range(N)).range([0, SPARK_W]).padding(0);
    const ySc = d3.scaleLinear().domain([1, 22]).range([PAD, SPARK_H - PAD]);
    const lineGen = d3.line()
      .defined(d => d !== null)
      .x((_, i) => xSc(i))
      .y(d => ySc(d))
      .curve(d3.curveCatmullRom.alpha(.5));

    DATA.clusters.forEach(cluster => {{
      const panel = document.createElement("div");
      panel.className = "panel";
      panel.innerHTML = `
        <div class="panel-header">
          <span class="panel-title" style="color:${{cluster.color}}">${{cluster.label}}</span>
          <span class="panel-count">${{cluster.n}} clubs</span>
        </div>
        <div class="panel-desc">${{cluster.desc}}</div>
      `;

      cluster.teams.forEach(team => {{
        const row = document.createElement("div");
        row.className = "club-row";

        const nameEl = document.createElement("div");
        nameEl.className = "club-name";
        nameEl.title = team.name;
        nameEl.textContent = team.name;

        const metaEl = document.createElement("div");
        metaEl.className = "club-meta";
        const badge = team.currently_in ? "●" : "○";
        metaEl.innerHTML = `${{team.n_seasons}}y&nbsp;<span title="stints" style="color:#444">${{team.stints}}×</span>&nbsp;<span style="color:${{team.currently_in ? cluster.color : "#333"}}">${{badge}}</span>`;

        const sparkWrap = document.createElement("div");
        sparkWrap.className = "spark-wrap";

        const svg = d3.create("svg")
          .attr("viewBox", `0 0 ${{SPARK_W}} ${{SPARK_H}}`)
          .attr("height", SPARK_H);

        // Season tick marks for every 5th season
        for (let i = 0; i < N; i += 5) {{
          svg.append("line")
            .attr("x1", xSc(i)).attr("x2", xSc(i))
            .attr("y1", 0).attr("y2", SPARK_H)
            .attr("stroke", "#ffffff08").attr("stroke-width", 1);
        }}

        // Ghost baseline at position 10
        svg.append("line")
          .attr("x1", 0).attr("x2", SPARK_W)
          .attr("y1", ySc(10)).attr("y2", ySc(10))
          .attr("stroke", "#ffffff06").attr("stroke-width", 0.5);

        // Relegation zone fill
        svg.append("rect")
          .attr("x", 0).attr("width", SPARK_W)
          .attr("y", ySc(17.5)).attr("height", ySc(22) - ySc(17.5))
          .attr("fill", "#ff000010");

        // The sparkline
        const pos = team.pos;
        svg.append("path")
          .datum(pos)
          .attr("fill", "none")
          .attr("stroke", cluster.color)
          .attr("stroke-width", 1.4)
          .attr("opacity", 0.85)
          .attr("d", lineGen);

        // Dot at last known position
        const lastIdx = pos.reduce((acc, p, i) => p !== null ? i : acc, -1);
        if (lastIdx >= 0) {{
          const isEnd = lastIdx === N - 1;
          svg.append("circle")
            .attr("cx", xSc(lastIdx))
            .attr("cy", ySc(pos[lastIdx]))
            .attr("r", isEnd ? 3.5 : 2.5)
            .attr("fill", isEnd ? cluster.color : "#555")
            .attr("stroke", "none");
        }}

        sparkWrap.appendChild(svg.node());
        row.appendChild(nameEl);
        row.appendChild(sparkWrap);
        row.appendChild(metaEl);
        panel.appendChild(row);
      }});

      document.getElementById("grid").appendChild(panel);
    }});
    </script>
    </body>
    </html>"""

    with open("trajectories.html", "w", encoding="utf-8") as f:
        f.write(HTML)
    logger.info("trajectories.html written")


if __name__ == "__main__":
    main()

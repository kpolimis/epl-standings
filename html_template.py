"""Build the self-contained HTML string for the animated EPL chart."""


def build_html(js_data: str, seasons: list[str]) -> str:
    """Return the full index.html content as a string.

    Args:
        js_data: JSON-serialised EPL payload (seasons, teams, raw).
        seasons: Ordered season labels used to derive subtitle counts.
    """
    epl = [s for s in seasons if "First Div" not in s]
    n_epl   = len(epl)
    min_epl = min(epl)
    max_epl = max(epl)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>EPL League Positions — Animated</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@900&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<script src="https://d3js.org/d3.v7.min.js"></script>
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{--bg:#07090d;--surface:#0d1117;--border:#21262d;--text:#c9d1d9;--muted:#6e7681;--accent:#3fb950}}
body{{background:var(--bg);color:var(--text);font-family:'IBM Plex Mono',monospace;
  display:flex;flex-direction:column;align-items:center;min-height:100vh;overflow-x:hidden}}
header{{width:100%;max-width:1440px;padding:28px 40px 0}}
h1{{font-family:'Playfair Display',serif;font-size:clamp(20px,2.6vw,38px);font-weight:900;
  color:#f0f4f8;letter-spacing:-.02em;line-height:1.1}}
h1 span{{color:var(--accent)}}
.subtitle{{font-size:11px;color:var(--muted);letter-spacing:.08em;text-transform:uppercase;padding-bottom:4px}}
#banner{{display:flex;align-items:center;gap:14px;padding:10px 20px 10px 14px;
  background:var(--surface);border:1px solid var(--border);border-radius:8px;
  margin:14px 40px 0;width:calc(100% - 80px);max-width:1360px;transition:border-color .4s;min-height:58px}}
#banner-logo{{width:36px;height:36px;border-radius:50%;object-fit:contain;
  background:#111;border:2px solid #333;flex-shrink:0}}
#banner-text{{flex:1;display:flex;flex-direction:column;gap:1px}}
#banner-season{{font-size:10px;color:var(--muted);letter-spacing:.1em;text-transform:uppercase}}
#banner-name{{font-size:15px;font-weight:600;transition:color .4s}}
#banner-suffix{{font-size:10px;color:var(--muted)}}
.zone-legend{{display:flex;align-items:center;gap:16px;flex-shrink:0}}
.zone-pip{{display:flex;align-items:center;gap:5px;font-size:9px;
  color:var(--muted);letter-spacing:.05em;white-space:nowrap}}
.zone-pip span{{width:10px;height:10px;border-radius:2px;flex-shrink:0}}
#chart-wrap{{width:100%;max-width:1440px;padding:10px 20px 0;overflow-x:auto}}
#chart svg{{display:block;width:100%;height:auto}}
#controls{{display:flex;align-items:center;gap:14px;flex-wrap:wrap;
  padding:14px 40px 20px;width:100%;max-width:1440px}}
.btn{{background:var(--surface);border:1px solid var(--border);color:var(--text);
  font-family:'IBM Plex Mono',monospace;font-size:12px;padding:7px 16px;border-radius:6px;
  cursor:pointer;transition:background .15s,border-color .15s;white-space:nowrap}}
.btn:hover{{background:#161b22;border-color:#444}}
.btn.active{{background:#1f6feb;border-color:#1f6feb;color:#fff}}
#play-btn{{font-size:14px;padding:7px 20px;min-width:90px}}
#play-btn.playing{{background:#238636;border-color:#238636;color:#fff}}
#slider-wrap{{flex:1;min-width:160px;display:flex;align-items:center;gap:10px}}
#slider{{-webkit-appearance:none;appearance:none;width:100%;height:4px;border-radius:4px;
  background:var(--border);outline:none;cursor:pointer}}
#slider::-webkit-slider-thumb{{-webkit-appearance:none;width:14px;height:14px;
  border-radius:50%;background:var(--accent);cursor:pointer}}
#season-lbl{{font-size:13px;font-weight:600;color:#f0f4f8;white-space:nowrap;min-width:72px}}
.speed-group{{display:flex;gap:4px}}
.speed-group .btn{{padding:5px 10px;font-size:11px}}
#roster{{width:100%;max-width:1440px;padding:0 40px 50px}}
#roster-hdr{{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;
  gap:12px;margin-bottom:14px;padding-top:4px;border-top:1px solid var(--border)}}
#roster-hdr h2{{font-family:'Playfair Display',serif;font-size:18px;font-weight:900;
  color:#f0f4f8;padding-top:14px}}
#roster-hdr h2 span{{color:var(--muted);font-size:13px;font-family:'IBM Plex Mono',monospace;
  font-weight:400;margin-left:6px}}
.sort-group{{display:flex;gap:4px;padding-top:14px}}
.sort-group .btn{{padding:4px 10px;font-size:10px}}
#team-grid{{display:flex;flex-wrap:wrap;gap:7px}}
.chip{{display:inline-flex;align-items:center;gap:7px;padding:5px 11px;
  background:var(--surface);border:1px solid var(--border);border-radius:20px;
  cursor:pointer;font-size:11px;color:var(--text);
  transition:background .12s,border-color .12s,transform .1s;user-select:none;--cc:#556070}}
.chip:hover{{background:#161b22;border-color:#555;transform:translateY(-1px)}}
.chip.selected{{border-color:var(--cc);background:color-mix(in srgb,var(--cc) 15%,transparent);color:#f0f4f8}}
.chip .dot{{width:7px;height:7px;border-radius:50%;background:var(--cc);flex-shrink:0}}
.chip .meta{{color:var(--muted);font-size:9px;margin-left:1px}}
.tip{{position:fixed;pointer-events:none;background:#161b22;border:1px solid #30363d;
  border-radius:6px;padding:10px 14px;font-size:12px;color:var(--text);
  box-shadow:0 8px 24px rgba(0,0,0,.6);z-index:999;display:none;line-height:1.7;max-width:240px}}
.tip strong{{display:block;color:#f0f4f8;font-size:13px;margin-bottom:1px}}
footer{{font-size:10px;color:#484f58;text-align:center;padding:4px 20px 30px;line-height:1.8}}
footer a{{color:#58a6ff;text-decoration:none}}
</style>
</head>
<body>
<header>
  <div>
    <h1>Premier League — <span>Every Season</span></h1>
    <p class="subtitle">{n_epl} Premier League seasons · {min_epl} – {max_epl}  (+ 1991/92 First Division context)</p>
  </div>
</header>
<div id="banner">
  <img id="banner-logo" src="" alt="">
  <div id="banner-text">
    <span id="banner-season">Season</span>
    <span id="banner-name">—</span>
    <span id="banner-suffix"></span>
  </div>
  <div class="zone-legend">
    <div class="zone-pip"><span style="background:#1f6feb55"></span>Champions League</div>
    <div class="zone-pip"><span style="background:#f59e0b55"></span>Europa League</div>
    <div class="zone-pip"><span style="background:#10b98155"></span>Conference League</div>
    <div class="zone-pip"><span style="background:#ff000033"></span>Relegation</div>
  </div>
</div>
<div id="chart-wrap"><div id="chart"></div></div>
<div id="controls">
  <button class="btn" id="reset-btn">↺</button>
  <button class="btn" id="play-btn">▶ Play</button>
  <div class="speed-group">
    <button class="btn speed-btn" data-ms="1400">0.5×</button>
    <button class="btn speed-btn active" data-ms="750">1×</button>
    <button class="btn speed-btn" data-ms="380">2×</button>
    <button class="btn speed-btn" data-ms="120">5×</button>
  </div>
  <div id="slider-wrap">
    <input type="range" id="slider" min="0" max="0" step="1" value="0">
  </div>
  <span id="season-lbl">1991/92 (First Div.)</span>
</div>
<section id="roster">
  <div id="roster-hdr">
    <h2>All EPL clubs <span id="club-count"></span></h2>
    <div class="sort-group">
      <button class="btn sort-btn active" data-sort="seasons">By seasons</button>
      <button class="btn sort-btn" data-sort="best">Best finish</button>
      <button class="btn sort-btn" data-sort="alpha">A–Z</button>
    </div>
  </div>
  <div id="team-grid"></div>
</section>
<div class="tip" id="tip"></div>
<footer>
  Data from football-data.co.uk and jalapic/engsoccerdata · {n_epl} verified seasons · 1991/92 First Division context included<br>
  <a href="https://github.com/kpolimis/epl-standings" target="_blank">github.com/kpolimis/epl-standings</a>
</footer>
<script>
const EPL = {js_data};

(function(){{
  const seasons = EPL.seasons;
  const teams   = EPL.teams;
  const N       = seasons.length;

  const champ = seasons.map(s => {{
    const e = Object.entries(EPL.raw[s]).find(([,v])=>v===1);
    return e ? e[0] : null;
  }});

  let frame=0, playing=false, speed=750, timer=null, selectedTeam=null;
  document.getElementById('slider').max = N - 1;

  // ── Dimensions ───────────────────────────────────────────────
  const TW=1380, TH=760, M={{t:70,r:200,b:68,l:46}};
  const W=TW-M.l-M.r, H=TH-M.t-M.b;

  const svg = d3.select("#chart").append("svg")
    .attr("viewBox",`0 0 ${{TW}} ${{TH}}`).attr("width","100%");
  const defs = svg.append("defs");

  const filt = defs.append("filter").attr("id","glow")
    .attr("x","-30%").attr("y","-30%").attr("width","160%").attr("height","160%");
  filt.append("feGaussianBlur").attr("stdDeviation","3").attr("result","b");
  const fm = filt.append("feMerge");
  fm.append("feMergeNode").attr("in","b");
  fm.append("feMergeNode").attr("in","SourceGraphic");

  const g = svg.append("g").attr("transform",`translate(${{M.l}},${{M.t}})`);

  // ── Scales ────────────────────────────────────────────────────
  const xSc = d3.scalePoint().domain(seasons).range([0,W]).padding(.05);
  const ySc = d3.scaleLinear().domain([.3,22.5]).range([0,H]);

  // ── Background shapes ─────────────────────────────────────────
  g.append("rect").attr("width",W).attr("height",H).attr("fill","#0d1117").attr("rx",4);

  // Relegation zone (static)
  g.append("rect").attr("x",0).attr("width",W).attr("y",ySc(17.5))
    .attr("height",ySc(22.5)-ySc(17.5)).attr("fill","#ff00000a");

  // European zone bands (dynamic — update each frame)
  const clBand   = g.append("rect").attr("x",0).attr("width",W).attr("fill","#1f6feb0d");
  const elBand   = g.append("rect").attr("x",0).attr("width",W).attr("fill","#f59e0b0b");
  const confBand = g.append("rect").attr("x",0).attr("width",W).attr("fill","#10b9810b");

  // Dynamic zone divider lines (CL/EL boundary)
  const clLine   = g.append("line").attr("x1",0).attr("x2",W)
    .attr("stroke","#1f6feb30").attr("stroke-width",.8).attr("stroke-dasharray","4,6");
  const elLine   = g.append("line").attr("x1",0).attr("x2",W)
    .attr("stroke","#f59e0b30").attr("stroke-width",.6).attr("stroke-dasharray","3,7");
  const confLine = g.append("line").attr("x1",0).attr("x2",W)
    .attr("stroke","#10b98130").attr("stroke-width",.6).attr("stroke-dasharray","3,7");

  // Dynamic zone labels
  const clLabel   = g.append("text").attr("x",W-8).attr("text-anchor","end")
    .attr("dominant-baseline","middle").attr("font-size",8.5)
    .attr("fill","#1f6feb35").attr("font-family","IBM Plex Mono,monospace");
  const elLabel   = g.append("text").attr("x",W-8).attr("text-anchor","end")
    .attr("dominant-baseline","middle").attr("font-size",8.5)
    .attr("fill","#f59e0b35").attr("font-family","IBM Plex Mono,monospace");
  const confLabel = g.append("text").attr("x",W-8).attr("text-anchor","end")
    .attr("dominant-baseline","middle").attr("font-size",8.5)
    .attr("fill","#10b98135").attr("font-family","IBM Plex Mono,monospace");

  // Static relegation label
  g.append("text").attr("x",W-8).attr("y",ySc(19.5))
    .attr("text-anchor","end").attr("dominant-baseline","middle")
    .attr("font-size",8.5).attr("fill","#ff000028").attr("font-family","IBM Plex Mono,monospace")
    .text("RELEGATION ZONE");

  // ── getZones — European spots by era ──────────────────────────
  // CL: 1 spot (1992/93-1996/97), 2 (1997/98-2002/03), 4 (2003/04+)
  // EL: positions cl+1 to 6 (UEFA Cup pre-2009, Europa League 2009+)
  // Conference League: position 7 only (2021/22+)
  function getZones(idx) {{
    if (idx === 0) return {{cl:0, el:0, conf:0}};          // pre-EPL, no European spots shown
    const cl   = idx <= 5 ? 1 : idx <= 11 ? 2 : 4;        // idx 1-5=1, 6-11=2, 12+=4
    const el   = Math.max(0, 6 - cl);                      // fills up to 6th
    const conf = idx >= 30 ? 1 : 0;                        // 2021/22 = index 30
    return {{cl, el, conf}};
  }}

  function updateZoneBands(idx, animate, dur, ease) {{
    const z = getZones(idx);

    function setBand(rect, line, label, topPos, botPos, labelTxt, visible) {{
      const bandTr  = animate ? rect.transition().duration(dur).ease(ease)  : rect;
      const lineTr  = animate ? line.transition().duration(dur).ease(ease)  : line;
      const labelTr = animate ? label.transition().duration(dur).ease(ease) : label;
      if (visible && botPos > topPos) {{
        const y = ySc(topPos), h = Math.max(0, ySc(botPos) - ySc(topPos));
        const mid = ySc((topPos + botPos) / 2);
        bandTr.attr("y",y).attr("height",h).attr("opacity",1);
        lineTr.attr("y1",ySc(topPos)).attr("y2",ySc(topPos)).attr("opacity",1);
        labelTr.attr("y", mid).text(labelTxt).attr("opacity",1);
      }} else {{
        bandTr.attr("height",0).attr("opacity",0);
        lineTr.attr("opacity",0);
        labelTr.attr("opacity",0);
      }}
    }}

    // Champions League band: pos 0.3 → cl+0.5
    const clTxt = idx <= 5 ? "CHAMPIONS LEAGUE (1 SPOT)" :
                  idx <= 11 ? "CHAMPIONS LEAGUE (2 SPOTS)" : "CHAMPIONS LEAGUE";
    setBand(clBand, clLine, clLabel, 0.3, z.cl + 0.5, clTxt, z.cl > 0);

    // Europa League band: pos cl+0.5 → cl+el+0.5
    const elTxt = idx <= 11 ? "UEFA CUP" : idx < 30 ? "EUROPA LEAGUE" : "EUROPA LEAGUE";
    setBand(elBand, elLine, elLabel, z.cl + 0.5, z.cl + z.el + 0.5, elTxt, z.el > 0);

    // Conference League band: pos cl+el+0.5 → cl+el+1.5 (only 2021/22+)
    const clBot = z.cl + z.el + 0.5;
    setBand(confBand, confLine, confLabel, clBot, clBot + 1, "CONFERENCE LEAGUE", z.conf > 0);
  }}

  [17].forEach(p => g.append("line").attr("x1",0).attr("x2",W).attr("y1",ySc(p)).attr("y2",ySc(p))
    .attr("stroke","#30363d").attr("stroke-width",.8).attr("stroke-dasharray","4,6"));
  [1,10,20].forEach(p => g.append("line").attr("x1",0).attr("x2",W).attr("y1",ySc(p)).attr("y2",ySc(p))
    .attr("stroke","#1a1f28").attr("stroke-width",.5));

  // Pre-EPL divider
  const divX = (xSc(seasons[0])+xSc(seasons[1]))/2;
  g.append("line").attr("x1",divX).attr("x2",divX).attr("y1",-18).attr("y2",H)
    .attr("stroke","#f0ad4e33").attr("stroke-width",1.5).attr("stroke-dasharray","5,4");
  g.append("text").attr("x",divX+6).attr("y",-8)
    .attr("text-anchor","start").attr("font-size",8)
    .attr("fill","#f0ad4e88").attr("font-family","IBM Plex Mono,monospace")
    .text("Premier League →");

  const playhead = g.append("line").attr("y1",0).attr("y2",H)
    .attr("stroke","#ffffff18").attr("stroke-width",1.5);

  // ── computeDisplayData ────────────────────────────────────────
  function computeDisplayData(rawPos, slice) {{
    let lastKnown=null, firstSeen=false, lastReal=null;
    const solid=[], full=[], realPts=[];
    for (let i=0; i<slice; i++) {{
      const p=rawPos[i];
      if (p!==null) {{
        solid.push(p); full.push(p);
        lastReal={{i,s:seasons[i],p}}; lastKnown=p; firstSeen=true;
      }} else if (firstSeen) {{
        solid.push(null); full.push(lastKnown);
      }} else {{
        solid.push(null); full.push(null);
      }}
    }}
    const isRelegd = firstSeen && rawPos[slice-1]===null;
    return {{solid,full,realPts:solid.map((p,i)=>p!==null?{{i,s:seasons[i],p}}:null).filter(Boolean),lastReal,isRelegd}};
  }}

  const lineGen = d3.line()
    .defined(d=>d!==null).x((_,i)=>xSc(seasons[i])).y(d=>ySc(d))
    .curve(d3.curveCatmullRom.alpha(.5));

  // ── Build paths and markers for ALL teams ─────────────────────
  const allNames = Object.keys(teams);
  const hlNames  = allNames.filter(t=>teams[t].hl);
  const bgNames  = allNames.filter(t=>!teams[t].hl);

  // Paths: bg teams
  const bgPaths={{}}, bgGhost={{}};
  bgNames.forEach(t => {{
    bgGhost[t] = g.append("path").attr("fill","none")
      .attr("stroke","#4a5568").attr("stroke-width",.5)
      .attr("stroke-dasharray","2,6").attr("opacity",.15);
    bgPaths[t] = g.append("path").attr("fill","none")
      .attr("stroke","#4a5568").attr("stroke-width",.8).attr("opacity",.22);
  }});

  // Paths: hl teams
  const hlGhost={{}}, hlPaths={{}}, hlDots={{}};
  hlNames.forEach(t => {{
    const c=teams[t].color;
    hlGhost[t]=g.append("path").attr("fill","none").attr("stroke",c)
      .attr("stroke-width",1.1).attr("stroke-dasharray","3,6").attr("opacity",.22);
    hlPaths[t]=g.append("path").attr("fill","none").attr("stroke",c)
      .attr("stroke-width",2.2).attr("opacity",.9).attr("filter","url(#glow)");
    hlDots[t]=g.append("g");
  }});

  // ── Marker groups — ALL teams get one ─────────────────────────
  // Structure: <g> → <circle> ring + <text> initials + <image> logo
  // Initials are always drawn; logo replaces them if it loads.
  const markerGrps={{}};

  allNames.forEach(t => {{
    const info=teams[t];
    const sn=t.replace(/[^a-zA-Z0-9]/g,"-");
    const r=info.hl?14:9;
    const fontSize=info.hl?8:6;
    const clipId=`clip-${{sn}}`;

    defs.append("clipPath").attr("id",clipId)
      .append("circle").attr("r",r-1);

    const grp=g.append("g")
      .style("opacity","0")
      .style("cursor","pointer")
      .on("mouseenter",ev=>showTip(ev,t))
      .on("mousemove",ev=>moveTip(ev))
      .on("mouseleave",hideTip);

    // Ring — white background for clubs whose badge needs a light canvas
    const bgFill = info.lightBadge ? "#ffffff" : "#0d1117";
    grp.append("circle").attr("r",r)
      .attr("fill",bgFill).attr("stroke",info.color)
      .attr("stroke-width",info.hl?1.8:1.2);

    // Initials text — always present as fallback
    grp.append("text").attr("class","initials")
      .attr("text-anchor","middle").attr("dominant-baseline","central")
      .attr("font-size",fontSize).attr("font-weight","600")
      .attr("font-family","IBM Plex Mono,monospace")
      .attr("fill",info.hl?info.color:"#9ca3af")
      .attr("pointer-events","none")
      .text(info.initials);

    // Logo image — hidden until loaded
    grp.append("image").attr("class","logo-img")
      .attr("href","").attr("x",-(r-1)).attr("y",-(r-1))
      .attr("width",(r-1)*2).attr("height",(r-1)*2)
      .attr("clip-path",`url(#${{clipId}})`)
      .attr("preserveAspectRatio","xMidYMid meet")
      .attr("pointer-events","none")
      .style("display","none");

    markerGrps[t]=grp;
  }});

  // Hit areas for hl teams (wide invisible stroke for easier hover)
  hlNames.forEach(t => {{
    g.append("path").attr("fill","none").attr("stroke","transparent")
      .attr("stroke-width",12).attr("class","hit").attr("data-team",t)
      .style("cursor","pointer")
      .on("mouseenter",ev=>showTip(ev,t))
      .on("mousemove",ev=>moveTip(ev))
      .on("mouseleave",hideTip);
  }});

  // ── Axes ──────────────────────────────────────────────────────
  const xAx=g.append("g").attr("transform",`translate(0,${{H}})`);
  xAx.call(d3.axisBottom(xSc).tickValues(seasons.filter((_,i)=>i%2===0)).tickSize(5))
     .select(".domain").remove();
  xAx.selectAll("text")
    .attr("transform","rotate(-40)").attr("text-anchor","end")
    .attr("dx","-4px").attr("dy","3px").attr("font-size",9)
    .attr("fill",d=>d.includes("First Div")?"#f0ad4e":"#6e7681")
    .attr("font-weight",d=>d.includes("First Div")?"600":"400")
    .attr("font-family","IBM Plex Mono,monospace");
  xAx.selectAll(".tick line").attr("stroke","#30363d");
  g.append("g").call(d3.axisLeft(ySc).tickValues(d3.range(1,23)).tickSize(0).tickFormat(d=>d))
   .select(".domain").remove();
  g.select("g").selectAll("text").attr("x",-9).attr("font-size",9)
    .attr("fill","#484f58").attr("font-family","IBM Plex Mono,monospace");

  // ── Tooltip ───────────────────────────────────────────────────
  const tip=document.getElementById("tip");

  function showTip(ev,name) {{
    const info=teams[name];
    const pts=info.pos.map((p,i)=>p!==null?{{s:seasons[i],p}}:null).filter(Boolean);
    const vis=pts.filter(d=>seasons.indexOf(d.s)<=frame);
    if (!vis.length) return;
    const cur=vis[vis.length-1];
    const best=vis.reduce((a,b)=>a.p<b.p?a:b);
    const ttls=vis.filter(d=>d.p===1).map(d=>d.s);
    let h=`<strong style="color:${{info.color}}">${{name}}</strong>`;
    const eplVis=vis.filter(d=>!d.s.includes("First Div"));
    h+=`${{cur.s}}: <b>P${{cur.p}}</b><br>${{eplVis.length}} EPL seasons`;
    if (ttls.length) h+=`<br>🏆 ${{ttls.join(", ")}}`;
    h+=`<br>Best: P${{best.p}} (${{best.s}})`;
    tip.innerHTML=h; tip.style.display="block"; moveTip(ev);
    dimAll(name);
  }}
  function moveTip(ev){{ tip.style.left=(ev.clientX+14)+"px"; tip.style.top=(ev.clientY-30)+"px"; }}
  function hideTip(){{ tip.style.display="none"; selectedTeam?dimAll(selectedTeam):undimAll(); }}

  // ── Dim/undim ─────────────────────────────────────────────────
  function setMarkerOpacity(t, op) {{
    markerGrps[t].interrupt().style("opacity", String(op));
  }}

  function dimAll(active) {{
    bgNames.forEach(t => {{
      const on=(t===active);
      bgPaths[t].attr("opacity",on?.85:.01).attr("stroke",on?"#88aadd":"#4a5568").attr("stroke-width",on?2:.8);
      bgGhost[t].attr("opacity",on?.5:.01);
      setMarkerOpacity(t, on?1:.04);
    }});
    hlNames.forEach(t => {{
      const on=(t===active);
      hlPaths[t].attr("opacity",on?1:.04);
      hlGhost[t].attr("opacity",on?.3:.01);
      hlDots[t].attr("opacity",on?1:.03);
      setMarkerOpacity(t, on?1:.04);
    }});
  }}

  function undimAll() {{
    bgNames.forEach(t => {{
      bgPaths[t].attr("opacity",.22).attr("stroke","#4a5568").attr("stroke-width",.8);
      bgGhost[t].attr("opacity",.15);
      const {{lastReal,isRelegd}}=computeDisplayData(teams[t].pos,frame+1);
      setMarkerOpacity(t, (lastReal&&isRelegd)?.7:(!isRelegd&&lastReal&&lastReal.i===frame)?.8:0);
    }});
    hlNames.forEach(t => {{
      hlPaths[t].attr("opacity",.9); hlGhost[t].attr("opacity",.22); hlDots[t].attr("opacity",1);
      const {{lastReal,isRelegd}}=computeDisplayData(teams[t].pos,frame+1);
      setMarkerOpacity(t, lastReal?(isRelegd?.85:1):0);
    }});
  }}

  // ── Banner ────────────────────────────────────────────────────
  const bannerEl=document.getElementById("banner");
  const bannerLogo=document.getElementById("banner-logo");
  const bannerSeason=document.getElementById("banner-season");
  const bannerName=document.getElementById("banner-name");
  const bannerSuffix=document.getElementById("banner-suffix");

  function updateBanner(idx) {{
    const s=seasons[idx], c=champ[idx], info=c?teams[c]:null;
    bannerSeason.textContent=s.includes("First Div")?"1991/92 First Division (pre-EPL)":s+" Champion";
    if (c&&info) {{
      bannerName.textContent="🏆 "+c; bannerName.style.color=info.color;
      bannerSuffix.textContent=`P1 of ${{Object.keys(EPL.raw[s]).length}} teams`;
      bannerEl.style.borderColor=info.color+"55";
      bannerLogo.dataset.team=c;
      const src=info.logo||"";
      if (src) {{ bannerLogo.src=src; bannerLogo.style.opacity="1"; bannerLogo.style.borderColor=info.color; }}
      else bannerLogo.style.opacity="0";
    }} else {{
      bannerName.textContent="—"; bannerName.style.color="#6e7681";
      bannerLogo.style.opacity="0"; bannerEl.style.borderColor="";
    }}
  }}

  // ── positionMarker — shared for all teams ─────────────────────
  // Marker always sits exactly on its season column — no rightward offset.
  // Active: column of current frame at their position.
  // Relegated: pinned at their last real season column, stays forever.
  function positionMarker(t, idx) {{
    const info=teams[t];
    const {{lastReal,isRelegd}}=computeDisplayData(info.pos, idx+1);
    const grp=markerGrps[t];
    grp.interrupt();

    if (!lastReal) {{ grp.style("opacity","0"); return; }}

    let lx, ly, targetOp;
    if (!isRelegd && lastReal.i===idx) {{
      lx = xSc(seasons[idx]);
      ly = ySc(lastReal.p);
      targetOp = "1";
    }} else if (isRelegd) {{
      lx = xSc(lastReal.s);
      ly = ySc(lastReal.p);
      targetOp = info.hl ? "0.85" : "0.75";
    }} else {{
      grp.style("opacity","0"); return;
    }}

    grp.attr("transform",`translate(${{lx}},${{ly}})`).style("opacity",targetOp);
  }}

  // ── renderFrame ───────────────────────────────────────────────
  function renderFrame(idx, animate) {{
    const dur=animate?Math.min(speed*.75,550):0, ease=d3.easeCubicInOut;
    const slice=idx+1;

    // Playhead
    playhead.attr("x1",xSc(seasons[idx])).attr("x2",xSc(seasons[idx]));

    document.getElementById("slider").value=idx;
    document.getElementById("season-lbl").textContent=seasons[idx];
    updateBanner(idx);
    updateZoneBands(idx, animate, dur, ease);

    // Background teams: solid line (breaks at relegation) + dashed ghost (carry-forward)
    bgNames.forEach(t => {{
      const {{solid,full}}=computeDisplayData(teams[t].pos,slice);
      (animate?bgPaths[t].transition().duration(dur).ease(ease):bgPaths[t]).attr("d",lineGen(solid));
      (animate?bgGhost[t].transition().duration(dur).ease(ease):bgGhost[t]).attr("d",lineGen(full));
    }});

    // Highlighted teams: solid + ghost + dots
    hlNames.forEach(t => {{
      const info=teams[t];
      const {{solid,full,realPts}}=computeDisplayData(info.pos,slice);

      (animate?hlPaths[t].transition().duration(dur).ease(ease):hlPaths[t]).attr("d",lineGen(solid));
      (animate?hlGhost[t].transition().duration(dur).ease(ease):hlGhost[t]).attr("d",lineGen(full));
      d3.selectAll(`.hit[data-team="${{t}}"]`).attr("d",lineGen(solid));

      hlDots[t].selectAll("circle").interrupt();
      const dots=hlDots[t].selectAll("circle").data(realPts,d=>d.i);
      dots.exit().remove();
      dots.enter().append("circle")
        .attr("cx",d=>xSc(d.s)).attr("cy",d=>ySc(d.p)).attr("r",0)
        .attr("fill",info.color).attr("opacity",.8)
        .transition().duration(300).ease(d3.easeBackOut).attr("r",d=>d.i===idx?4.5:2.2);
      dots.transition().duration(dur).ease(ease)
        .attr("cx",d=>xSc(d.s)).attr("cy",d=>ySc(d.p)).attr("r",d=>d.i===idx?4.5:2.2);
    }});

    // All markers
    allNames.forEach(t => positionMarker(t, idx));

    if (selectedTeam) dimAll(selectedTeam);
  }}

  // ── Playback ──────────────────────────────────────────────────
  function step(){{ if(!playing)return; if(frame>=N-1){{pause();return;}} frame++; renderFrame(frame,true); timer=setTimeout(step,speed); }}
  function play(){{ if(frame>=N-1)frame=0; playing=true; document.getElementById("play-btn").textContent="⏸ Pause"; document.getElementById("play-btn").classList.add("playing"); timer=setTimeout(step,speed); }}
  function pause(){{ playing=false; clearTimeout(timer); document.getElementById("play-btn").textContent="▶ Play"; document.getElementById("play-btn").classList.remove("playing"); }}

  document.getElementById("play-btn").addEventListener("click",()=>playing?pause():play());
  document.getElementById("reset-btn").addEventListener("click",()=>{{pause();frame=0;renderFrame(0,false);}});
  document.getElementById("slider").addEventListener("input",function(){{pause();frame=+this.value;renderFrame(frame,false);}});
  document.querySelectorAll(".speed-btn").forEach(b=>b.addEventListener("click",function(){{
    document.querySelectorAll(".speed-btn").forEach(x=>x.classList.remove("active"));
    this.classList.add("active"); speed=+this.dataset.ms;
  }}));
  document.addEventListener("keydown",ev=>{{
    if(ev.code==="Space"){{ev.preventDefault();playing?pause():play();}}
    if(ev.code==="ArrowRight"&&!playing){{frame=Math.min(frame+1,N-1);renderFrame(frame,true);}}
    if(ev.code==="ArrowLeft"&&!playing){{frame=Math.max(frame-1,0);renderFrame(frame,true);}}
  }});

  // ── Roster table ──────────────────────────────────────────────
  function eplSeasons(t){{ return teams[t].pos.slice(1).filter(p=>p!==null).length; }}
  function allSeasons(t){{ return teams[t].pos.filter(p=>p!==null).length; }}
  function bestFinish(t){{ const ps=teams[t].pos.filter(p=>p!==null); return ps.length?Math.min(...ps):99; }}

  let sortKey="seasons";
  function buildRoster(){{
    // Include ALL teams that appear in any season (including pre-EPL)
    const list=Object.keys(teams).filter(t=>allSeasons(t)>0)
      .map(t=>(({{t,
        seasons:eplSeasons(t),
        preEPLOnly: eplSeasons(t)===0,
        best:bestFinish(t),
        color:teams[t].color,
        hl:teams[t].hl}})));
    if(sortKey==="alpha") list.sort((a,b)=>a.t.localeCompare(b.t));
    else if(sortKey==="best") list.sort((a,b)=>a.best-b.best||b.seasons-a.seasons);
    else list.sort((a,b)=>b.seasons-a.seasons||a.t.localeCompare(b.t));
    document.getElementById("club-count").textContent=`— ${{list.length}} clubs`;
    const grid=document.getElementById("team-grid");
    grid.innerHTML="";
    list.forEach(d=>{{
      const chip=document.createElement("div");
      chip.className="chip"+(selectedTeam===d.t?" selected":"");
      chip.style.setProperty("--cc",d.color);
      chip.dataset.team=d.t;
      const seasonsLabel = d.preEPLOnly
        ? `pre-EPL only · P${{d.best}}`
        : `${{d.seasons}}y · P${{d.best}}`;
      chip.innerHTML=`<span class="dot"></span><span>${{d.t}}</span><span class="meta">${{seasonsLabel}}</span>`;
      chip.addEventListener("click",()=>toggleSelect(d.t));
      grid.appendChild(chip);
    }});
  }}

  function toggleSelect(team){{
    selectedTeam=(selectedTeam===team)?null:team;
    selectedTeam?dimAll(selectedTeam):undimAll();
    document.querySelectorAll(".chip").forEach(c=>c.classList.toggle("selected",c.dataset.team===selectedTeam));
    document.getElementById("chart-wrap").scrollIntoView({{behavior:"smooth",block:"nearest"}});
  }}

  document.querySelectorAll(".sort-btn").forEach(b=>b.addEventListener("click",function(){{
    document.querySelectorAll(".sort-btn").forEach(x=>x.classList.remove("active"));
    this.classList.add("active"); sortKey=this.dataset.sort; buildRoster();
  }}));

  // ── Logo resolution — direct URL first, REST API fallback ───────
  // Initials are always visible; logo replaces them only if it loads cleanly.
  async function resolveLogos(){{
    const probe=src=>new Promise(res=>{{
      const img=new Image(); img.onload=()=>res(src); img.onerror=()=>res(null); img.src=src;
    }});

    const tasks=Object.entries(markerGrps).map(async([team,grp])=>{{
      const info=teams[team];
      const imgEl=grp.select("image.logo-img");
      if (imgEl.empty()) return;

      let src=null;

      // 1. Try direct URL if provided
      if (info.logo) src=await probe(info.logo);

      // 2. REST API fallback
      if (!src && info.wiki) {{
        try {{
          const resp=await fetch(
            `https://en.wikipedia.org/api/rest_v1/page/summary/${{info.wiki}}`,
            {{headers:{{"Api-User-Agent":"EPL-chart/1.0 (kpolimis)"}}}}
          );
          if (resp.ok) {{
            const data=await resp.json();
            // Prefer SVG (club badge) over JPG (might be stadium/player photo)
            const orig=data?.originalimage?.source||"";
            const thumb=data?.thumbnail?.source||"";
            const candidate=orig.endsWith(".svg")?orig:thumb.endsWith(".svg")?thumb:orig||thumb;
            if (candidate) src=await probe(candidate);
          }}
        }} catch(e){{}}
      }}

      if (src) {{
        info.logo=src;
        imgEl.attr("href",src).style("display",null);
        grp.select("text.initials").style("display","none");
        const bl=document.getElementById("banner-logo");
        if (bl.dataset.team===team){{ bl.src=src; bl.style.opacity="1"; }}
      }}
      // If no src: initials stay visible (already rendered)
    }});
    Promise.allSettled(tasks);
  }}

  // ── Init ──────────────────────────────────────────────────────
  renderFrame(0,false);
  buildRoster();
  resolveLogos();
}})();
</script>
</body>
</html>"""

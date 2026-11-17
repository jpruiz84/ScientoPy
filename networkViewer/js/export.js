/* Exports: images (neon PNG, publication SVG/PNG), crawl-tour videos and
   data files (VOSviewer, GEXF, CSV, JSON). Everything runs in the browser. */

function exportBaseName(app) {
  const m = app.data.meta;
  return slug(m.criterion[0].toUpperCase() + m.criterion.slice(1) + "_network" + (m.title ? "_" + m.title : ""));
}

function exportCaption(app) {
  const d = app.data, m = d.meta;
  return "ScientoPy · " + m.criterionLabel + " co-occurrence · " + m.startYear + "–" + m.endYear +
    " · " + fmtInt(d.n) + " items · " + d.clusters.length + " clusters";
}

/* ── neon PNG: a high resolution render of the current view ─ */

function exportPng(app, scale) {
  const W = app.cssW, H = app.cssH;
  scale = Math.min(scale, 8192 / Math.max(W, H));
  app.renderAtScale(scale);
  const out = document.createElement("canvas");
  out.width = Math.round(W * scale);
  out.height = Math.round(H * scale);
  const ctx = out.getContext("2d");
  ctx.drawImage(app.glCanvas, 0, 0, out.width, out.height);
  ctx.drawImage(app.ovCanvas, 0, 0, out.width, out.height);
  app.renderAtScale(0);
  ctx.setTransform(out.width / W, 0, 0, out.height / H, 0, 0);
  drawCanvasLegend(ctx, app, W, H, "dark");
  out.toBlob((blob) => {
    download(exportBaseName(app) + "_" + Math.round(scale) + "x.png", blob);
    app.hud.toast("PNG saved · " + out.width + "×" + out.height);
  }, "image/png");
}

function drawCanvasLegend(ctx, app, W, H, theme) {
  const d = app.data, light = theme === "light";
  const ink = light ? "rgba(30,34,40,0.9)" : "rgba(220,226,232,0.85)";
  ctx.textBaseline = "middle";
  ctx.font = "11px " + MONO;
  ctx.fillStyle = ink;
  ctx.fillText(exportCaption(app), 16, H - 16);
  if (app.settings.view === "network" || app.settings.view === "density") {
    const shown = d.clusters.slice(0, 12);
    shown.forEach((c, k) => {
      const y = H - 40 - (shown.length - 1 - k) * 16;
      ctx.fillStyle = light ? rgbToHex(darken(c.rgb)) : c.color;
      ctx.beginPath();
      ctx.arc(21, y, 4.5, 0, TAU);
      ctx.fill();
      ctx.fillStyle = ink;
      ctx.fillText(truncate(c.label, 34) + "  (" + c.members.length + ")", 32, y);
    });
  } else {
    const stops = light ? RAMP_VIRIDIS : RAMP_NEON;
    const g = ctx.createLinearGradient(16, 0, 196, 0);
    stops.forEach((s, k) => g.addColorStop(k / (stops.length - 1), rgbToHex(s)));
    ctx.fillStyle = g;
    ctx.fillRect(16, H - 46, 180, 8);
    ctx.fillStyle = ink;
    const lo = app.settings.view === "year" ? d.yearLo.toFixed(1) : "0";
    const hi = app.settings.view === "year" ? d.yearHi.toFixed(1) : fmtNum(d.citesHi);
    ctx.fillText(lo, 16, H - 30);
    ctx.textAlign = "right";
    ctx.fillText(hi, 196, H - 30);
    ctx.textAlign = "left";
    ctx.fillText(app.settings.view === "year" ? "avg. publication year" : "avg. citations", 16, H - 60);
  }
}

function darken(rgb) { return mixRgb(rgb, [0, 0, 0], 0.18); }

/* ── SVG: vector map of the current projection ─────────── */

function buildSvg(app, theme) {
  const d = app.data, f = app.frame, s = app.settings;
  const W = app.cssW, H = app.cssH, light = theme === "light";
  const view = s.view === "density" ? "network" : s.view;
  const color = (i) => {
    const nd = d.nodes[i];
    if (view === "year") return ramp(light ? RAMP_VIRIDIS : RAMP_NEON, (nd.avgYear - d.yearLo) / (d.yearHi - d.yearLo));
    if (view === "cites") return ramp(light ? RAMP_VIRIDIS : RAMP_NEON, Math.log1p(nd.avgCit) / Math.log1p(d.citesHi));
    return light ? darken(d.clusters[nd.c].rgb) : d.clusters[nd.c].rgb;
  };
  const visible = (i) => f.proj[i * 3 + 2] > 0 && f.vis[i] > 0.5;
  const P = (v) => v.toFixed(1);
  const out = [];
  out.push('<svg xmlns="http://www.w3.org/2000/svg" width="' + W + '" height="' + H + '" viewBox="0 0 ' + W + " " + H + '" font-family="Menlo, Consolas, DejaVu Sans Mono, monospace">');
  out.push("<title>" + escapeHtml(exportCaption(app)) + "</title>");
  out.push('<rect width="100%" height="100%" fill="' + (light ? "#ffffff" : "#07080b") + '"/>');

  out.push('<g fill="none" stroke-linecap="round">');
  const maxW = d.max.weight;
  const limit = Math.min(d.links.length, s.maxLinks);
  for (let k = 0; k < limit; k++) {
    const [i, j, w] = d.links[k];
    if (!visible(i) || !visible(j)) continue;
    const wn = Math.sqrt(w / maxW);
    const c = mixRgb(color(i), color(j), 0.5);
    out.push('<line x1="' + P(f.proj[i * 3]) + '" y1="' + P(f.proj[i * 3 + 1]) + '" x2="' + P(f.proj[j * 3]) + '" y2="' + P(f.proj[j * 3 + 1]) +
      '" stroke="' + rgbToHex(c) + '" stroke-opacity="' + (light ? 0.1 + 0.45 * wn : 0.12 + 0.5 * wn).toFixed(2) + '" stroke-width="' + (0.4 + 2.2 * wn).toFixed(2) + '"/>');
  }
  out.push("</g>");

  const order = [];
  for (let i = 0; i < d.n; i++) if (visible(i)) order.push(i);
  order.sort((a, b) => f.proj[b * 3 + 2] - f.proj[a * 3 + 2]);
  out.push("<g>");
  for (const i of order) {
    const c = rgbToHex(color(i));
    out.push('<circle cx="' + P(f.proj[i * 3]) + '" cy="' + P(f.proj[i * 3 + 1]) + '" r="' + P(Math.max(1.5, f.radius[i])) + '" fill="' + c +
      '" fill-opacity="' + (light ? 0.85 : 0.9) + '" stroke="' + (light ? "#ffffff" : c) + '" stroke-width="' + (light ? 0.8 : 0) + '"><title>' + escapeHtml(d.nodes[i].label) + "</title></circle>");
  }
  out.push("</g>");

  out.push('<g dominant-baseline="central">');
  for (const L of app.overlay.labels) {
    const c = color(L.i), cy = P(L.y + L.h / 2);
    if (L.kind === "plain" || L.kind === "flagdim") {
      out.push('<text x="' + P(L.x) + '" y="' + cy + '" font-size="' + L.size + '" fill="' + (light ? "#1f2329" : rgbToHex(mixRgb(c, [1, 1, 1], 0.55))) +
        '" paint-order="stroke" stroke="' + (light ? "#ffffff" : "#07080b") + '" stroke-width="3" stroke-opacity="0.8">' + escapeHtml(L.text) + "</text>");
    } else {
      const flag = L.kind === "flag";
      const box = flag ? "#ff5d6c" : light ? "#ffffff" : "#08090c";
      out.push('<rect x="' + P(L.x) + '" y="' + P(L.y) + '" width="' + P(L.w) + '" height="' + P(L.h) + '" fill="' + box + '" stroke="' + (flag ? "#ff5d6c" : rgbToHex(c)) + '" stroke-width="1"/>');
      out.push('<text x="' + P(L.x + 4) + '" y="' + cy + '" font-size="' + L.size + '" fill="' + (flag ? "#0b0c10" : light ? "#1f2329" : rgbToHex(c)) + '">' + escapeHtml(L.text) + "</text>");
    }
  }
  for (const co of app.overlay.callouts) {
    const c = d.clusters[co.c];
    out.push('<text x="' + P(co.x) + '" y="' + P(co.y + co.big / 2) + '" font-size="' + co.big + '" font-weight="700" fill="' + rgbToHex(light ? darken(c.rgb) : c.rgb) + '">' + escapeHtml(co.title) + "</text>");
  }
  out.push("</g>");

  // caption and legend
  const ink = light ? "#1f2329" : "#dce2e8";
  out.push('<g font-size="11" fill="' + ink + '" dominant-baseline="central">');
  out.push('<text x="16" y="' + (H - 16) + '">' + escapeHtml(exportCaption(app)) + "</text>");
  if (view === "network") {
    const shown = d.clusters.slice(0, 12);
    shown.forEach((c, k) => {
      const y = H - 40 - (shown.length - 1 - k) * 16;
      out.push('<circle cx="21" cy="' + y + '" r="4.5" fill="' + rgbToHex(light ? darken(c.rgb) : c.rgb) + '"/>');
      out.push('<text x="32" y="' + y + '">' + escapeHtml(truncate(c.label, 34) + "  (" + c.members.length + ")") + "</text>");
    });
  } else {
    const stops = light ? RAMP_VIRIDIS : RAMP_NEON;
    out.push('<defs><linearGradient id="lg">' + stops.map((st, k) => '<stop offset="' + (k / (stops.length - 1)).toFixed(3) + '" stop-color="' + rgbToHex(st) + '"/>').join("") + "</linearGradient></defs>");
    out.push('<rect x="16" y="' + (H - 46) + '" width="180" height="8" fill="url(#lg)"/>');
    out.push('<text x="16" y="' + (H - 60) + '">' + (view === "year" ? "avg. publication year" : "avg. citations") + "</text>");
    out.push('<text x="16" y="' + (H - 30) + '">' + (view === "year" ? d.yearLo.toFixed(1) : "0") + "</text>");
    out.push('<text x="196" y="' + (H - 30) + '" text-anchor="end">' + (view === "year" ? d.yearHi.toFixed(1) : fmtNum(d.citesHi)) + "</text>");
  }
  out.push("</g></svg>");
  return out.join("\n");
}

// Vector exports re-place the labels at screen scale, without HUD panels or crawler marks
function cleanSvg(app, theme) {
  app.renderAtScale(1, "clean");
  const svg = buildSvg(app, theme);
  app.renderAtScale(0);
  return svg;
}

function exportSvg(app, theme) {
  if (app.settings.view === "density") app.hud.toast("density is raster only: the SVG uses cluster colors", 3200);
  download(exportBaseName(app) + "_" + theme + ".svg", cleanSvg(app, theme), "image/svg+xml;charset=utf-8");
}

function exportPngLight(app) {
  const svg = cleanSvg(app, "light"), scale = 3;
  const url = URL.createObjectURL(new Blob([svg], { type: "image/svg+xml;charset=utf-8" }));
  const img = new Image();
  img.onload = () => {
    const c = document.createElement("canvas");
    c.width = app.cssW * scale;
    c.height = app.cssH * scale;
    const ctx = c.getContext("2d");
    ctx.drawImage(img, 0, 0, c.width, c.height);
    URL.revokeObjectURL(url);
    try {
      c.toBlob((blob) => {
        download(exportBaseName(app) + "_light.png", blob);
        app.hud.toast("PNG saved · " + c.width + "×" + c.height);
      }, "image/png");
    } catch (e) {
      app.hud.toast("this browser blocks SVG rasterizing: use the SVG export", 3500);
    }
  };
  img.onerror = () => app.hud.toast("could not rasterize the SVG: use the SVG export", 3500);
  img.src = url;
}

/* ── data ─────────────────────────────────────────────── */

const numStr = (v) => (v == null ? "" : Number.isInteger(v) ? String(v) : String(+v.toFixed(4)));
const cleanField = (s) => String(s).replace(/[\t\r\n]+/g, " ");
const csvField = (v) => {
  const s = v == null ? "" : String(v);
  return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
};

function vosviewerFiles(d) {
  const map = ["id\tlabel\tx\ty\tcluster\tweight<Links>\tweight<Total link strength>\tweight<Occurrences>\tscore<Avg. pub. year>\tscore<Avg. citations>"];
  for (const nd of d.nodes) {
    map.push([nd.id, cleanField(nd.label), nd.p2[0].toFixed(4), nd.p2[1].toFixed(4), nd.c + 1, nd.links, numStr(nd.tls), nd.occ, numStr(nd.avgYear), numStr(nd.avgCit)].join("\t"));
  }
  const net = d.links.map(([i, j, w]) => d.nodes[i].id + "\t" + d.nodes[j].id + "\t" + numStr(w));
  return { map: map.join("\n") + "\n", network: net.join("\n") + "\n" };
}

function gexfFile(d) {
  const x = (s) => escapeHtml(s);
  const out = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<gexf xmlns="http://gexf.net/1.3" xmlns:viz="http://gexf.net/1.3/viz" version="1.3">',
    "  <meta><creator>ScientoPy " + x(d.meta.version) + "</creator><description>" + x(d.meta.criterionLabel + " co-occurrence network") + "</description></meta>",
    '  <graph defaultedgetype="undirected" mode="static">',
    '    <attributes class="node">',
    '      <attribute id="0" title="cluster" type="integer"/>',
    '      <attribute id="1" title="occurrences" type="integer"/>',
    '      <attribute id="2" title="avg_pub_year" type="double"/>',
    '      <attribute id="3" title="avg_citations" type="double"/>',
    '      <attribute id="4" title="total_link_strength" type="double"/>',
    "    </attributes>",
    "    <nodes>",
  ];
  for (const nd of d.nodes) {
    const c = d.clusters[nd.c].rgb.map((v) => Math.round(v * 255));
    out.push('      <node id="' + nd.id + '" label="' + x(nd.label) + '"><attvalues><attvalue for="0" value="' + (nd.c + 1) + '"/><attvalue for="1" value="' + nd.occ +
      '"/><attvalue for="2" value="' + numStr(nd.avgYear || 0) + '"/><attvalue for="3" value="' + numStr(nd.avgCit) + '"/><attvalue for="4" value="' + numStr(nd.tls) +
      '"/></attvalues><viz:color r="' + c[0] + '" g="' + c[1] + '" b="' + c[2] + '"/><viz:position x="' + (nd.p2[0] * 500).toFixed(2) + '" y="' + (-nd.p2[1] * 500).toFixed(2) +
      '" z="0"/><viz:size value="' + (4 + 26 * Math.sqrt(nd.occ / d.max.occ)).toFixed(2) + '"/></node>');
  }
  out.push("    </nodes>", "    <edges>");
  d.links.forEach(([i, j, w], k) => out.push('      <edge id="' + k + '" source="' + d.nodes[i].id + '" target="' + d.nodes[j].id + '" weight="' + numStr(w) + '"/>'));
  out.push("    </edges>", "  </graph>", "</gexf>");
  return out.join("\n") + "\n";
}

function csvFiles(d) {
  const head = ["Id", "Label", "Cluster", "Cluster label", "Occurrences", "Links", "Total link strength", "Avg. pub. year", "Avg. citations", "hIndex", "AGR", "PDLY", "First year", "x", "y", "x3", "y3", "z3"].concat(d.years);
  const nodes = [head.join(",")];
  for (const nd of d.nodes) {
    nodes.push([nd.id, nd.label, nd.c + 1, d.clusters[nd.c].label, nd.occ, nd.links, numStr(nd.tls), nd.avgYear, nd.avgCit, nd.h, nd.agr, nd.pdly, nd.firstYear]
      .concat(nd.p2, nd.p3, nd.y).map(csvField).join(","));
  }
  const links = ["Source,Target,Source label,Target label,Weight"];
  for (const [i, j, w] of d.links) links.push([d.nodes[i].id, d.nodes[j].id, d.nodes[i].label, d.nodes[j].label, numStr(w)].map(csvField).join(","));
  return { nodes: nodes.join("\n") + "\n", links: links.join("\n") + "\n" };
}

function exportData(app, kind) {
  const d = app.data, base = exportBaseName(app);
  if (kind === "vos") {
    const f = vosviewerFiles(d);
    download(base + "_vosviewer_map.txt", f.map);
    setTimeout(() => download(base + "_vosviewer_network.txt", f.network), 400);
    app.hud.toast("VOSviewer map + network saved");
  } else if (kind === "gexf") {
    download(base + ".gexf", gexfFile(d), "application/xml;charset=utf-8");
    app.hud.toast("GEXF saved");
  } else if (kind === "csv") {
    const f = csvFiles(d);
    download(base + "_nodes.csv", f.nodes, "text/csv;charset=utf-8");
    setTimeout(() => download(base + "_links.csv", f.links, "text/csv;charset=utf-8"), 400);
    app.hud.toast("CSV nodes + links saved");
  } else if (kind === "json") {
    download(base + ".json", JSON.stringify(d.raw), "application/json");
    app.hud.toast("JSON saved");
  }
}

/* ── video: records the full crawl tour ─────────────────── */

const VIDEO_SIZES = { "16x9": [1920, 1080], "9x16": [1080, 1920], "1x1": [1080, 1080] };

class Recorder {
  constructor(app, aspect) {
    this.app = app;
    [this.W, this.H] = VIDEO_SIZES[aspect] || VIDEO_SIZES["16x9"];
    this.aspect = aspect;
  }

  static mimeType() {
    if (typeof MediaRecorder === "undefined") return null;
    const types = ["video/mp4;codecs=avc1.640028", "video/mp4", "video/webm;codecs=vp9", "video/webm;codecs=vp8", "video/webm"];
    return types.find((t) => MediaRecorder.isTypeSupported(t)) || null;
  }

  start() {
    const app = this.app;
    this.mime = Recorder.mimeType();
    if (!this.mime || !HTMLCanvasElement.prototype.captureStream) {
      app.hud.toast("video recording is not supported in this browser", 3500);
      return false;
    }
    this.canvas = document.createElement("canvas");
    this.canvas.width = this.W;
    this.canvas.height = this.H;
    this.ctx = this.canvas.getContext("2d");
    this.ctx.fillStyle = "#07080b";
    this.ctx.fillRect(0, 0, this.W, this.H);
    const stream = this.canvas.captureStream(30);
    this.chunks = [];
    this.rec = new MediaRecorder(stream, { mimeType: this.mime, videoBitsPerSecond: 16e6 });
    this.rec.ondataavailable = (e) => { if (e.data && e.data.size) this.chunks.push(e.data); };
    this.rec.onstop = () => this.save();
    app.recorder = this;
    app.setRenderOverride(this.W, this.H);
    document.body.classList.add("recording");
    document.getElementById("rec").hidden = false;
    this.t0 = performance.now();
    this.stopAt = 0;
    app.select(-1);
    app.setFollow(true);
    app.setCrawler(true);
    app.restartCrawl();
    this.rec.start(500);
    return true;
  }

  frame() {
    this.ctx.drawImage(this.app.glCanvas, 0, 0, this.W, this.H);
    this.ctx.drawImage(this.app.ovCanvas, 0, 0, this.W, this.H);
    const secs = (performance.now() - this.t0) / 1000;
    document.getElementById("rec-time").textContent = fmtClock(secs);
    if (this.app.crawler.state === "complete" && !this.stopAt) this.stopAt = secs + 3;
    if ((this.stopAt && secs >= this.stopAt) || secs > 600) this.stop();
  }

  stop() {
    if (!this.rec || this.rec.state === "inactive") return;
    this.rec.stop();
    const app = this.app;
    app.recorder = null;
    app.setRenderOverride(0, 0);
    document.body.classList.remove("recording");
    document.getElementById("rec").hidden = true;
  }

  save() {
    const ext = this.mime.indexOf("mp4") >= 0 ? "mp4" : "webm";
    const blob = new Blob(this.chunks, { type: this.mime.split(";")[0] });
    download(exportBaseName(this.app) + "_crawl_" + this.aspect + "." + ext, blob);
    this.app.hud.toast("video saved · " + (blob.size / 1e6).toFixed(1) + " MB " + ext, 3500);
  }
}

function runExport(app, kind) {
  if (kind === "png2") exportPng(app, 2);
  else if (kind === "png4") exportPng(app, 4);
  else if (kind === "png-light") exportPngLight(app);
  else if (kind === "svg-light") exportSvg(app, "light");
  else if (kind === "svg-dark") exportSvg(app, "dark");
  else if (kind.indexOf("video-") === 0) new Recorder(app, kind.slice(6)).start();
  else exportData(app, kind);
}

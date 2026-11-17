/* App core: state, animation loop, input and control wiring. */

const REDUCED_MOTION = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

const app = {
  data: null, settings: null, camera: null, renderer: null, overlay: null, crawler: null, hud: null,
  recorder: null, selected: -1, hover: -1,
  cssW: 1, cssH: 1, pr: 1, scaleOverride: 0, renderOverride: null,
  time: 0, introT: 0, morph: 0, userZoom: 1, yearF: 0,
};

function initApp() {
  const raw = JSON.parse(document.getElementById("sp-data").textContent);
  const d = (app.data = prepareData(raw));
  const narrow = window.innerWidth < 760;
  app.settings = {
    view: "network", space: "3d", sizeBy: "occ",
    maxLinks: Math.min(1000, d.totalLinks), labelBudget: Math.min(d.n, d.n > 150 ? 36 : 60), dust: 1,
    yearIdx: d.nYears - 1, timelinePlaying: false,
    crawler: true, crawlerPlaying: !REDUCED_MOTION, speed: 1, follow: true, loop: true,
    callouts: true, hud: !narrow, autoRotate: !REDUCED_MOTION,
  };
  app.glCanvas = document.getElementById("gl");
  app.ovCanvas = document.getElementById("ov");
  app.camera = new Camera();
  app.renderer = new Renderer(app.glCanvas, d);
  app.overlay = new Overlay(app.ovCanvas, app);

  const n = d.n;
  app.radius = new Float32Array(n);
  app.colors = new Float32Array(n * 3);
  app.states = new Float32Array(n * 4);
  app.vis = new Float32Array(n);
  app.emph = new Float32Array(n);
  app.frame = { proj: new Float32Array(n * 3), radius: new Float32Array(n), vis: app.vis, bySize: [], pr: 1, w: 1, h: 1, time: 0, intro: 0 };
  d.nodes.forEach((nd, i) => {
    app.colors.set(nd.rgb || d.clusters[nd.c].rgb, i * 3);
    app.vis[i] = 1;
    app.emph[i] = 1;
  });

  app.hud = new Hud(app);
  app.crawler = new Crawler(app);
  app.hud.refreshClusters();
  app.hud.setCluster(app.crawler.current);
  if (!app.settings.hud) document.body.classList.add("nohud");

  wireControls();
  wireInput();
  resize();
  window.addEventListener("resize", resize);

  // intro: the map unfolds while the camera swings in
  const cam = app.camera;
  cam.cur.dist = cam.homeDist * 2.3;
  cam.cur.yaw = -1.1;
  cam.cur.pitch = 0.55;
  cam.goal.dist = cam.homeDist * 0.95;
  cam.rate = 1.1;
  app.last = performance.now();
  requestAnimationFrame(tick);
}

/* ── geometry helpers shared with the crawler and overlay ─ */

app.introAt = function (delay) {
  const t = clamp((app.introT - delay) / 0.9, 0, 1);
  return 1 - Math.pow(1 - t, 3);
};

app.worldPos = function (i, out) {
  const nd = app.data.nodes[i], m = app.morph;
  const x = lerp(nd.p3[0], nd.p2[0], m) * WORLD_SCALE;
  const y = lerp(nd.p3[1], nd.p2[1], m) * WORLD_SCALE;
  const z = nd.p3[2] * (1 - m) * WORLD_SCALE;
  const e = app.introAt(app.renderer.nodeData[(app.renderer.texW + i) * 4 + 2] + 0.15);
  const a = (1 - e) * 2.4, c = Math.cos(a), s = Math.sin(a);
  out[0] = (c * x - s * z) * e;
  out[1] = y * e;
  out[2] = (s * x + c * z) * e;
  return out;
};

app.nodeColor = (i) => [app.colors[i * 3], app.colors[i * 3 + 1], app.colors[i * 3 + 2]];
app.focusNode = () => (app.selected >= 0 ? app.selected : app.hover);

/* ── per frame ─────────────────────────────────────────── */

const tmp3 = [0, 0, 0];
let nbCache = { focus: -2, set: null };
let sizeOrderKey = "";

function tick(now) {
  const dt = clamp((now - app.last) / 1000, 0, 0.05);
  app.last = now;
  step(dt);
  draw(dt);
  if (app.recorder) app.recorder.frame();
  requestAnimationFrame(tick);
}

function step(dt) {
  const s = app.settings, d = app.data;
  app.time += dt;
  if (app.introT < 1.6) app.introT = Math.min(1.6, app.introT + dt * 0.6);
  app.morph = approach(app.morph, s.space === "2d" ? 1 : 0, 3.2, dt);
  if (Math.abs(app.morph - (s.space === "2d" ? 1 : 0)) < 1e-3) app.morph = s.space === "2d" ? 1 : 0;

  if (s.timelinePlaying) {
    app.yearF += dt * clamp(d.nYears / 12, 0.8, 3);
    if (app.yearF >= d.nYears - 1) { app.yearF = d.nYears - 1; setTimeline(false); }
    setYear(Math.floor(app.yearF), true);
  }

  if (s.crawler && s.crawlerPlaying && app.introT > 0.45) app.crawler.update(dt * s.speed);
  cameraDirector(dt);
  app.camera.update(dt, s.space === "2d");
  updateNodeStates(dt);
  app.renderer.updateNodes(app.radius, app.colors, app.states);
}

function cameraDirector(dt) {
  const s = app.settings, cam = app.camera, cr = app.crawler;
  if (s.follow && s.crawler && cr.state === "complete") {
    cam.flyTo(0, 0, 0, cam.homeDist * app.userZoom, 1.2);
  } else if (s.follow && s.crawler && cr.state !== "idle") {
    const p = cr.position(tmp3);
    const between = cr.state === "travel" && cr.silk && cr.silk.life > 0.4;
    const zoom = (between ? 0.92 : 0.74) * app.userZoom;
    cam.flyTo(p[0] * 0.86, p[1] * 0.86, p[2] * 0.86, cam.homeDist * zoom, app.introT < 1.2 ? 1.1 : 1.4);
  }
  if (s.autoRotate && s.follow && s.space === "3d" && !app.dragging) cam.goal.yaw += dt * 0.055;
}

function updateNodeStates(dt) {
  const d = app.data, s = app.settings, cr = app.crawler, n = d.n;
  const yi = s.yearIdx, year = d.years[yi];
  const focus = app.focusNode();
  if (nbCache.focus !== focus) nbCache = { focus, set: focus >= 0 ? new Set(d.adj[focus].map((a) => a[0])) : null };
  const crawlMode = s.crawler;
  const overlayView = s.view === "year" || s.view === "cites";
  for (let i = 0; i < n; i++) {
    const nd = d.nodes[i];
    app.vis[i] = approach(app.vis[i], nd.firstYear <= year ? 1 : 0, 5, dt);
    const v = clamp(sizeValue(d, nd, s.sizeBy, yi), 0, 1);
    app.radius[i] = approach(app.radius[i] || 0, 2.2 + 15 * Math.sqrt(v), 6, dt);

    const status = crawlMode ? cr.status[nd.c] : "done";
    let rgb;
    if (s.view === "year") rgb = ramp(RAMP_NEON, (nd.avgYear - d.yearLo) / (d.yearHi - d.yearLo));
    else if (s.view === "cites") rgb = ramp(RAMP_NEON, Math.log1p(nd.avgCit) / Math.log1p(d.citesHi));
    else rgb = status === "queued" && crawlMode ? greyOf(d.clusters[nd.c].rgb, 0.85) : d.clusters[nd.c].rgb;
    const o = i * 3;
    app.colors[o] = approach(app.colors[o], rgb[0], 4, dt);
    app.colors[o + 1] = approach(app.colors[o + 1], rgb[1], 4, dt);
    app.colors[o + 2] = approach(app.colors[o + 2], rgb[2], 4, dt);

    let em = 1;
    if (crawlMode) {
      em = status === "reading" ? (cr.read[i] ? 1.45 : 1.15) : status === "done" ? 0.92 : 0.55;
      if (overlayView) em = Math.max(em, 0.85);
    }
    app.emph[i] = approach(app.emph[i], em, 3, dt);

    const q = i * 4;
    app.states[q] = app.vis[i];
    app.states[q + 1] = app.emph[i];
    app.states[q + 2] = i === focus ? 1 : nbCache.set && nbCache.set.has(i) ? 0.5 : 0;
    app.states[q + 3] = crawlMode ? cr.read[i] : 0;
  }
}

function computeProjection() {
  const d = app.data, f = app.frame, cam = app.camera;
  for (let i = 0; i < d.n; i++) {
    app.worldPos(i, tmp3);
    cam.project(tmp3[0], tmp3[1], tmp3[2], f.proj, i * 3);
    const w = f.proj[i * 3 + 2];
    const persp = clamp(cam.homeDist / Math.max(w, 1), 0.35, 3.5);
    f.radius[i] = app.radius[i] * persp * app.vis[i] * app.introAt(app.renderer.nodeData[(app.renderer.texW + i) * 4 + 2] + 0.15);
  }
  const key = app.settings.sizeBy + ":" + app.settings.yearIdx;
  if (key !== sizeOrderKey) {
    sizeOrderKey = key;
    const s = app.settings;
    f.bySize = d.nodes.map((nd, i) => [i, sizeValue(d, nd, s.sizeBy, s.yearIdx)]).sort((a, b) => b[1] - a[1]).map((a) => a[0]);
  }
}

function draw(dt) {
  const s = app.settings, cam = app.camera, f = app.frame, cr = app.crawler;
  computeProjection();
  f.pr = app.pr; f.w = app.cssW; f.h = app.cssH; f.time = app.time; f.intro = app.introT;

  // the spider walks in screen space on top of its world position
  if (s.crawler && cr.to >= 0) {
    cr.position(tmp3);
    const out = [0, 0, 0];
    cam.project(tmp3[0], tmp3[1], tmp3[2], out, 0);
    let y = out[1];
    if (cr.state === "drop") y = lerp(-60, out[1], cr.dropProgress);
    const R = 14 * clamp(Math.pow(cam.homeDist / Math.max(out[2], 1), 0.45), 0.7, 1.6);
    cr.spider.update(Math.max(dt, 1e-3), out[0], y, R);
  }

  app.renderer.render({
    vp: cam.vp, morph: app.morph, time: app.time, intro: app.introT, pr: app.pr,
    focal: cam.homeDist, fov: cam.fov, view: s.view, dust: s.dust,
    maxRank: s.maxLinks, edgeAlpha: s.space === "3d" ? 0.42 : 0.5, hlActive: app.focusNode() >= 0,
  });
  app.overlay.draw(f);
  app.hud.tick(dt);
}

/* ── actions ───────────────────────────────────────────── */

app.select = function (i, fly) {
  app.selected = i;
  if (i >= 0) {
    app.hud.showNode(i);
    if (fly) {
      app.worldPos(i, tmp3);
      setFollow(false);
      app.camera.flyTo(tmp3[0], tmp3[1], tmp3[2], app.camera.homeDist * 0.5);
    }
  } else {
    app.hud.hideNode();
  }
};

app.goToCluster = function (k) {
  const d = app.data;
  if (k < 0 || k >= d.clusters.length) return;
  if (app.settings.crawler) {
    app.crawler.jumpTo(k);
    setFollow(true);
    if (!app.settings.crawlerPlaying) setPlaying(true);
  } else {
    const c = d.clusters[k];
    let x = 0, y = 0, z = 0;
    c.members.forEach((i) => { app.worldPos(i, tmp3); x += tmp3[0]; y += tmp3[1]; z += tmp3[2]; });
    const m = c.members.length;
    app.camera.flyTo(x / m, y / m, z / m, app.camera.homeDist * 0.6);
    app.hud.setCluster(k);
  }
};

app.restartCrawl = function () {
  app.crawler.reset();
  app.hud.refreshClusters();
  app.hud.setCluster(app.crawler.current);
  setCrawler(true);
  setPlaying(true);
};

app.setCrawler = setCrawler;
app.setFollow = setFollow;

function setCrawler(on) {
  app.settings.crawler = on;
  if (!on) setPlaying(false);
  syncButtons();
}

function setPlaying(on) {
  if (on && !app.settings.crawler) app.settings.crawler = true;
  app.settings.crawlerPlaying = on;
  syncButtons();
}

function setFollow(on) {
  app.settings.follow = on;
  if (on) app.userZoom = 1;
  syncButtons();
}

function setTimeline(on) {
  const s = app.settings, d = app.data;
  if (on) {
    if (s.yearIdx >= d.nYears - 1) {
      const first = Math.min(...d.nodes.map((nd) => nd.firstYear));
      app.yearF = Math.max(0, first - d.years[0]);
    } else app.yearF = s.yearIdx;
    setYear(Math.floor(app.yearF), true);
  }
  s.timelinePlaying = on;
  document.getElementById("b-timeline").innerHTML = on ? "&#10074;&#10074;" : "&#9654;";
}

function setYear(idx, fromTimeline) {
  const s = app.settings, d = app.data;
  s.yearIdx = clamp(idx, 0, d.nYears - 1);
  if (!fromTimeline) app.yearF = s.yearIdx;
  const r = document.getElementById("r-year");
  r.value = s.yearIdx;
  document.getElementById("v-year").textContent = s.yearIdx < d.nYears - 1 ? "≤ " + d.years[s.yearIdx] : "all · " + d.years[d.nYears - 1];
}

function setView(v) {
  app.settings.view = v;
  app.hud.updateLegend();
  syncButtons();
}

function setSpace(v) {
  app.settings.space = v;
  if (v === "2d") app.camera.goal.pitch = 0;
  else if (Math.abs(app.camera.goal.pitch) < 0.05) { app.camera.goal.pitch = 0.22; app.camera.goal.yaw += 0.5; app.camera.rate = 2; }
  syncButtons();
}

function toggleHud(force) {
  const s = app.settings;
  s.hud = force != null ? force : !s.hud;
  document.body.classList.toggle("nohud", !s.hud);
  resize();
}

function syncButtons() {
  const s = app.settings;
  document.querySelectorAll(".seg").forEach((seg) => {
    const key = seg.dataset.ctl;
    const val = key === "view" ? s.view : key === "space" ? s.space : key === "size" ? s.sizeBy : String(s.speed);
    seg.querySelectorAll("button").forEach((b) => b.classList.toggle("on", b.dataset.v === val));
  });
  const play = document.getElementById("b-play");
  play.textContent = s.crawler && s.crawlerPlaying ? "pause" : "play";
  play.classList.toggle("on", s.crawler && s.crawlerPlaying);
  document.getElementById("b-follow").classList.toggle("on", s.follow);
  document.getElementById("b-hud").classList.toggle("on", s.hud);
}

/* ── controls ──────────────────────────────────────────── */

function wireControls() {
  const s = app.settings, d = app.data, $ = (id) => document.getElementById(id);

  document.querySelectorAll(".seg").forEach((seg) => {
    seg.addEventListener("click", (e) => {
      const b = e.target.closest("button");
      if (!b) return;
      const key = seg.dataset.ctl, v = b.dataset.v;
      if (key === "view") setView(v);
      else if (key === "space") setSpace(v);
      else if (key === "size") { s.sizeBy = v; syncButtons(); }
      else if (key === "speed") { s.speed = parseFloat(v); syncButtons(); }
    });
  });

  const links = $("r-links");
  links.max = d.totalLinks;
  links.value = s.maxLinks;
  const showLinks = () => { $("v-links").textContent = fmtInt(s.maxLinks) + " / " + fmtInt(d.totalLinks); };
  links.addEventListener("input", () => { s.maxLinks = +links.value; showLinks(); });
  showLinks();

  const labels = $("r-labels");
  labels.max = Math.min(200, d.n);
  labels.value = s.labelBudget;
  const showLabels = () => { $("v-labels").textContent = s.labelBudget; };
  labels.addEventListener("input", () => { s.labelBudget = +labels.value; showLabels(); });
  showLabels();

  const dust = $("r-dust");
  dust.value = Math.round(s.dust * 100);
  const showDust = () => { $("v-dust").textContent = Math.round(s.dust * 100) + "%"; };
  dust.addEventListener("input", () => { s.dust = +dust.value / 100; showDust(); });
  showDust();

  const year = $("r-year");
  year.min = 0;
  year.max = d.nYears - 1;
  year.addEventListener("input", () => { setTimeline(false); setYear(+year.value); });
  setYear(s.yearIdx);
  $("b-timeline").addEventListener("click", () => setTimeline(!s.timelinePlaying));

  $("b-play").addEventListener("click", () => setPlaying(!(s.crawler && s.crawlerPlaying)));
  $("b-restart").addEventListener("click", () => app.restartCrawl());
  $("b-follow").addEventListener("click", () => setFollow(!s.follow));
  $("b-hud").addEventListener("click", () => toggleHud());
  $("b-help").addEventListener("click", () => { $("help").hidden = false; });
  $("help-close").addEventListener("click", () => { $("help").hidden = true; });
  $("help").addEventListener("click", (e) => { if (e.target.id === "help") $("help").hidden = true; });
  $("ctl-toggle").addEventListener("click", toggleControls);

  const menu = $("exportmenu");
  $("b-export").addEventListener("click", () => { menu.hidden = !menu.hidden; $("b-export").classList.toggle("on", !menu.hidden); });
  menu.addEventListener("click", (e) => {
    const b = e.target.closest("button");
    if (!b) return;
    menu.hidden = true;
    $("b-export").classList.remove("on");
    runExport(app, b.dataset.x);
  });
  $("rec-stop").addEventListener("click", () => app.recorder && app.recorder.stop());

  const search = $("search");
  const find = () => {
    const q = search.value.trim().toLowerCase();
    if (!q) return;
    let i = d.nodes.findIndex((nd) => nd.lower === q);
    if (i < 0) i = d.nodes.findIndex((nd) => nd.lower.startsWith(q));
    if (i < 0) i = d.nodes.findIndex((nd) => nd.lower.includes(q));
    if (i >= 0) { app.select(i, true); search.blur(); }
    else app.hud.toast("no item matches “" + search.value + "”");
  };
  search.addEventListener("change", find);
  search.addEventListener("keydown", (e) => { if (e.key === "Enter") find(); });

  syncButtons();
}

function toggleControls() {
  const c = document.getElementById("controls");
  c.classList.toggle("collapsed");
  document.getElementById("ctl-toggle").innerHTML = c.classList.contains("collapsed") ? "+" : "&minus;";
}

/* ── pointer, wheel and keyboard ───────────────────────── */

function pick(x, y) {
  const f = app.frame, d = app.data;
  let best = -1, bestScore = Infinity;
  for (let i = 0; i < d.n; i++) {
    const o = i * 3;
    if (f.proj[o + 2] <= 0 || app.vis[i] < 0.5) continue;
    const dx = f.proj[o] - x, dy = f.proj[o + 1] - y;
    const r = Math.max(f.radius[i], 4) + 4;
    const d2 = dx * dx + dy * dy;
    if (d2 < r * r && d2 / (r * r) < bestScore) { bestScore = d2 / (r * r); best = i; }
  }
  return best;
}

function wireInput() {
  const ov = app.ovCanvas;
  const pointers = new Map();
  let start = null, moved = false, lastClick = { t: 0, i: -1 }, pinch = null;

  ov.addEventListener("contextmenu", (e) => e.preventDefault());
  ov.addEventListener("pointerdown", (e) => {
    if (app.recorder) return;
    ov.setPointerCapture(e.pointerId);
    pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (pointers.size === 1) {
      start = { x: e.clientX, y: e.clientY, button: e.button, shift: e.shiftKey };
      moved = false;
    } else if (pointers.size === 2) {
      const [a, b] = [...pointers.values()];
      pinch = { d: Math.hypot(a.x - b.x, a.y - b.y), cx: (a.x + b.x) / 2, cy: (a.y + b.y) / 2 };
      moved = true;
    }
  });
  ov.addEventListener("pointermove", (e) => {
    const p = pointers.get(e.pointerId);
    if (!p) {
      if (app.recorder) return;
      const i = pick(e.clientX, e.clientY);
      app.hover = i;
      ov.classList.toggle("pointer", i >= 0);
      app.hud.tooltip(i, e.clientX, e.clientY);
      return;
    }
    const dx = e.clientX - p.x, dy = e.clientY - p.y;
    p.x = e.clientX; p.y = e.clientY;
    if (pointers.size === 2 && pinch) {
      const [a, b] = [...pointers.values()];
      const dist = Math.hypot(a.x - b.x, a.y - b.y), cx = (a.x + b.x) / 2, cy = (a.y + b.y) / 2;
      if (dist > 0 && pinch.d > 0) app.camera.zoom(pinch.d / dist);
      app.camera.pan(cx - pinch.cx, cy - pinch.cy);
      pinch = { d: dist, cx, cy };
      setFollow(false);
      return;
    }
    if (!moved && Math.hypot(e.clientX - start.x, e.clientY - start.y) > 4) {
      moved = true;
      app.dragging = true;
      ov.classList.add("dragging");
      setFollow(false);
      app.hover = -1;
      app.hud.tooltip(-1);
    }
    if (!moved) return;
    if (app.settings.space === "2d" || start.button === 2 || start.shift) app.camera.pan(dx, dy);
    else app.camera.orbit(dx, dy);
  });
  const end = (e) => {
    if (!pointers.has(e.pointerId)) return;
    pointers.delete(e.pointerId);
    if (pointers.size < 2) pinch = null;
    if (pointers.size) return;
    ov.classList.remove("dragging");
    app.dragging = false;
    if (!moved && e.type === "pointerup") {
      const i = pick(e.clientX, e.clientY);
      const now = performance.now();
      if (i >= 0 && lastClick.i === i && now - lastClick.t < 350) app.select(i, true);
      else app.select(i, false);
      lastClick = { t: now, i };
    }
  };
  ov.addEventListener("pointerup", end);
  ov.addEventListener("pointercancel", end);
  ov.addEventListener("pointerleave", () => { if (!pointers.size) { app.hover = -1; app.hud.tooltip(-1); } });

  ov.addEventListener("wheel", (e) => {
    e.preventDefault();
    const factor = Math.exp(clamp(e.deltaY, -200, 200) * 0.0015);
    if (app.settings.follow && app.settings.crawler) app.userZoom = clamp(app.userZoom * factor, 0.25, 3);
    else app.camera.zoom(factor);
  }, { passive: false });

  window.addEventListener("keydown", (e) => {
    const $ = (id) => document.getElementById(id);
    if (e.target instanceof HTMLInputElement && e.target.type !== "range") {
      if (e.key === "Escape") e.target.blur();
      return;
    }
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    const s = app.settings, d = app.data;
    switch (e.key) {
      case " ": e.preventDefault(); setPlaying(!(s.crawler && s.crawlerPlaying)); break;
      case "ArrowRight": app.goToCluster((app.crawler.current + 1) % d.clusters.length); break;
      case "ArrowLeft": app.goToCluster((app.crawler.current - 1 + d.clusters.length) % d.clusters.length); break;
      case "2": setSpace("2d"); break;
      case "3": setSpace("3d"); break;
      case "n": case "N": setView("network"); break;
      case "y": case "Y": setView("year"); break;
      case "d": case "D": setView("density"); break;
      case "t": case "T": setTimeline(!s.timelinePlaying); break;
      case "f": case "F": setFollow(!s.follow); break;
      case "r": case "R": app.restartCrawl(); break;
      case "l": case "L": {
        const steps = [0, Math.min(d.n, 36), Math.min(d.n, 120)];
        s.labelBudget = steps[(steps.indexOf(s.labelBudget) + 1) % steps.length] || 0;
        $("r-labels").value = s.labelBudget;
        $("v-labels").textContent = s.labelBudget;
        break;
      }
      case "h": case "H": toggleHud(); break;
      case "c": case "C": toggleControls(); break;
      case "e": case "E": $("b-export").click(); break;
      case "/": e.preventDefault(); $("search").focus(); break;
      case "?": $("help").hidden = !$("help").hidden; break;
      case "Escape":
        if (app.recorder) app.recorder.stop();
        $("help").hidden = true;
        $("exportmenu").hidden = true;
        $("b-export").classList.remove("on");
        app.select(-1);
        break;
    }
  });
}

/* ── sizing ────────────────────────────────────────────── */

function resize() {
  const s = app.settings, cam = app.camera;
  const oldHome = cam.homeDist;
  let pads;
  if (app.renderOverride) {
    // videos render at ~1.6x so labels stay readable on a phone
    const [W, H] = app.renderOverride;
    app.pr = Math.min(W, H) / 675;
    app.cssW = W / app.pr; app.cssH = H / app.pr;
    const k = Math.min(window.innerWidth / W, window.innerHeight / H) * 0.94;
    for (const c of [app.glCanvas, app.ovCanvas]) { c.style.width = W * k + "px"; c.style.height = H * k + "px"; }
    pads = { top: app.cssH * 0.17, bottom: app.cssH * 0.2 };
  } else {
    app.cssW = window.innerWidth; app.cssH = window.innerHeight;
    app.pr = app.scaleOverride || Math.min(window.devicePixelRatio || 1, 2);
    for (const c of [app.glCanvas, app.ovCanvas]) { c.style.width = ""; c.style.height = ""; }
    const dash = s.hud ? document.getElementById("dash").offsetHeight || 0 : 0;
    pads = { top: 58, bottom: dash ? dash + 6 : 12, left: 0, right: window.innerWidth > 1000 ? 120 : 0 };
  }
  const W = Math.round(app.cssW * app.pr), H = Math.round(app.cssH * app.pr);
  app.renderer.resize(W, H);
  app.overlay.resize(W, H);
  cam.setViewport(app.cssW, app.cssH, pads);
  cam.homeDist = cam.fitDistance(WORLD_SCALE * 1.05);
  if (oldHome && oldHome !== cam.homeDist) {
    const k = cam.homeDist / oldHome;
    cam.goal.dist *= k;
    cam.cur.dist *= k;
  }
  cam.computeMatrices();
}

// mode: "neon" keeps the live look (spider, crawler labels), "clean" places
// plain labels only; both ignore the on-screen HUD panels
app.renderAtScale = function (scale, mode) {
  app.scaleOverride = scale || 0;
  app.exporting = scale ? mode || "neon" : null;
  resize();
  draw(0);
};

app.setRenderOverride = function (w, h) {
  app.renderOverride = w ? [w, h] : null;
  resize();
};

/* ── boot ──────────────────────────────────────────────── */

try {
  initApp();
} catch (err) {
  const box = document.getElementById("fatal");
  box.hidden = false;
  box.innerHTML = "<div><b>The network map could not start.</b><br><br>" + escapeHtml(err.message || String(err)) +
    "<br><br><span class='dim'>It needs a browser with WebGL2: a recent Chrome, Edge, Firefox or Safari, with hardware acceleration enabled.</span></div>";
  console.error(err);
}

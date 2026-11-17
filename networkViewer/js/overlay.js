/* 2D overlay: labels, cluster callouts, flags, selection, the spider and the
   recording HUD. Drawn on a canvas on top of the WebGL canvas. */

const FLAG_RED = hexToRgb("#ff5d6c");
const MONO = getComputedStyle(document.documentElement).getPropertyValue("--mono") || "monospace";

class Overlay {
  constructor(canvas, app) {
    this.canvas = canvas;
    this.ctx = canvas.getContext("2d");
    this.app = app;
    this.widths = new Map();
    this.labels = [];     // last placed labels, reused by the SVG export
    this.callouts = [];
  }

  resize(w, h) {
    if (this.canvas.width !== w || this.canvas.height !== h) {
      this.canvas.width = w;
      this.canvas.height = h;
    }
  }

  textWidth(text, size, bold) {
    const key = (bold ? "b" : "") + size + "|" + text;
    let w = this.widths.get(key);
    if (w == null) {
      this.ctx.font = (bold ? "700 " : "") + size + "px " + MONO;
      w = this.ctx.measureText(text).width;
      if (this.widths.size > 6000) this.widths.clear();
      this.widths.set(key, w);
    }
    return w;
  }

  draw(f) {
    const ctx = this.ctx, app = this.app, d = app.data, s = app.settings, cr = app.crawler;
    ctx.setTransform(f.pr, 0, 0, f.pr, 0, 0);
    ctx.clearRect(0, 0, f.w, f.h);
    if (f.intro < 0.35) {
      if (s.crawler && cr.state === "drop") this.drawSpider(f);
      if (app.recorder) this.drawBroadcast(f);
      return;
    }
    const fade = clamp((f.intro - 0.35) / 0.6, 0, 1);
    const rects = this.hudRects();
    const fits = (x, y, w, h) => {
      if (x < 4 || y < 4 || x + w > f.w - 4 || y + h > f.h - 4) return false;
      for (const r of rects) if (x < r[0] + r[2] && x + w > r[0] && y < r[1] + r[3] && y + h > r[1]) return false;
      return true;
    };

    this.callouts = s.callouts ? this.drawCallouts(f, rects, fade) : [];

    const proj = f.proj, rad = f.radius, vis = f.vis;
    const placed = new Uint8Array(d.n);
    const labels = [];
    const focus = app.focusNode();
    const cur = cr.current;
    const tryLabel = (i, kind, force) => {
      if (placed[i]) return;
      const o = i * 3;
      if (proj[o + 2] <= 0 || vis[i] < 0.5) return;
      const nd = d.nodes[i];
      const boxed = kind !== "plain" && kind !== "flagdim";
      const size = boxed || kind === "flagdim" ? 10.5 : Math.round(10 + 3.5 * Math.sqrt(nd.occ / d.max.occ));
      const text = kind === "flag" || kind === "flagdim" ? "⚑ " + nd.label : nd.label;
      const tw = this.textWidth(text, size, kind === "focus");
      const bw = tw + (boxed ? 8 : 0), bh = size + (boxed ? 6 : 2);
      const r = rad[i] + 4;
      let x = proj[o] + r, y = proj[o + 1] - bh / 2;
      if (!fits(x, y, bw, bh)) {
        x = proj[o] - r - bw;
        if (!fits(x, y, bw, bh)) {
          x = proj[o] - bw / 2; y = proj[o + 1] - r - bh;
          if (!fits(x, y, bw, bh) && !force) return;
        }
      }
      rects.push([x - 2, y - 1, bw + 4, bh + 2]);
      placed[i] = 1;
      labels.push({ i, kind, x, y, w: bw, h: bh, size, text, depth: proj[o + 2] });
    };

    const clean = app.exporting === "clean";
    if (!clean) {
      if (focus >= 0) tryLabel(focus, "focus", true);
      if (app.hover >= 0 && app.hover !== focus) tryLabel(app.hover, "focus", true);
      if (s.crawler && cr.to >= 0) tryLabel(cr.to, "read", true);
      if (s.crawler) {
        for (const tn of cr.tentacles) if (tn.fired) tryLabel(tn.node, tn.kind === "link" ? "link" : "read", false);
      }
      // flags of the active cluster are boxed, older ones stay as quiet red text
      for (const [i] of cr.flagged) if (d.nodes[i].c === cur) tryLabel(i, "flag", false);
      for (const [i] of cr.flagged) if (d.nodes[i].c !== cur) tryLabel(i, "flagdim", false);
    }
    if (!clean && s.crawler && cur >= 0) {
      let k = 0;
      for (const i of d.clusters[cur].members) {
        if (cr.read[i]) { tryLabel(i, "read", false); if (++k > 40) break; }
      }
    }
    let budget = s.labelBudget;
    for (const i of f.bySize) {
      if (labels.length >= budget + 12) break;
      if (budget <= 0) break;
      if (!placed[i]) { tryLabel(i, "plain", false); if (placed[i]) budget--; }
    }

    this.labels = labels;
    if (!clean) this.drawSelection(f, focus);
    this.drawLabels(f, labels, fade);
    if (s.crawler && !clean) this.drawSpider(f);
    if (app.recorder) this.drawBroadcast(f);
  }

  // Screen rectangles covered by HUD panels; labels stay out of them
  hudRects() {
    if (this.app.recorder || this.app.exporting) return [];
    const out = [];
    for (const id of ["topbar", "tabs", "titleblock", "controls", "dash", "nodepanel", "legend"]) {
      const e = document.getElementById(id);
      if (!e || e.hidden || e.offsetParent === null) continue;
      const r = e.getBoundingClientRect();
      if (r.width && r.height && getComputedStyle(e).opacity !== "0") out.push([r.left - 6, r.top - 6, r.width + 12, r.height + 12]);
    }
    return out;
  }

  drawCallouts(f, rects, fade) {
    const ctx = this.ctx, app = this.app, d = app.data, cr = app.crawler, s = app.settings;
    const out = [];
    const mc = [0, 0, 0];
    app.camera.project(0, 0, 0, mc, 0);
    // the active cluster is placed first so it always gets its spot
    const order = d.clusters.slice().sort((a, b) => (cr.status[b.index] === "reading") - (cr.status[a.index] === "reading"));
    for (const c of order) {
      if (c.members.length < 2 && d.clusters.length > 1) continue;
      let sw = 0, sx = 0, sy = 0, sxx = 0, syy = 0;
      for (const i of c.members) {
        const o = i * 3;
        if (f.proj[o + 2] <= 0 || f.vis[i] < 0.5) continue;
        const w = Math.sqrt(d.nodes[i].occ), px = f.proj[o], py = f.proj[o + 1];
        sw += w; sx += px * w; sy += py * w; sxx += px * px * w; syy += py * py * w;
      }
      if (sw <= 0) continue;
      const cx = sx / sw, cy = sy / sw;
      const spread = Math.sqrt(Math.max(0, sxx / sw - cx * cx) + Math.max(0, syy / sw - cy * cy));
      let dx = cx - mc[0], dy = cy - mc[1];
      const dl = Math.hypot(dx, dy);
      if (dl < 1) { dx = 0; dy = -1; } else { dx /= dl; dy /= dl; }
      const status = s.crawler ? cr.status[c.index] : "done";
      const title = truncate(c.label.toLowerCase(), 30);
      const sub = s.crawler
        ? cr.clusterRead[c.index] + "/" + c.members.length + " nodes · " + status
        : c.members.length + " nodes · " + fmtInt(c.docs) + " docs";
      const big = status === "reading" ? 17 : 14;
      const tw = Math.max(this.textWidth(title, big, true), this.textWidth(sub, 10, false));
      const h = big + 16;
      let x = 0, y = 0, ok = false;
      for (const reach of [1.05, 1.5, 2.0]) {
        const ax = cx + dx * (spread * reach + 16), ay = cy + dy * (spread * reach + 16);
        x = dx < -0.35 ? ax - tw : dx > 0.35 ? ax : ax - tw / 2;
        y = dy < 0 ? ay - h : ay;
        ok = x > 6 && y > 6 && x + tw < f.w - 6 && y + h < f.h - 6;
        for (const r of rects) if (ok && x < r[0] + r[2] && x + tw > r[0] && y < r[1] + r[3] && y + h > r[1]) ok = false;
        if (ok) break;
      }
      if (!ok) continue;
      rects.push([x - 4, y - 2, tw + 8, h + 4]);
      const col = status === "reading" ? rgba(c.rgb, fade) : status === "done" ? rgba([0.92, 0.94, 0.96], 0.85 * fade) : rgba([0.62, 0.65, 0.7], 0.6 * fade);
      ctx.textBaseline = "top";
      ctx.font = "700 " + big + "px " + MONO;
      ctx.fillStyle = col;
      if (status === "reading") { ctx.shadowColor = rgba(c.rgb, 0.6); ctx.shadowBlur = 12; }
      ctx.fillText(title, x, y);
      ctx.shadowBlur = 0;
      ctx.font = "10px " + MONO;
      ctx.fillStyle = rgba([0.55, 0.58, 0.63], 0.85 * fade);
      ctx.fillText(sub, x, y + big + 3);
      out.push({ c: c.index, x, y, title, sub, big, status });
    }
    return out;
  }

  drawLabels(f, labels, fade) {
    const ctx = this.ctx, d = this.app.data, s = this.app.settings;
    ctx.textBaseline = "middle";
    const homeW = this.app.camera.homeDist;
    for (const L of labels) {
      const nd = d.nodes[L.i], crgb = this.app.nodeColor(L.i);
      const cy = L.y + L.h / 2;
      if (L.kind === "flagdim") {
        ctx.font = L.size + "px " + MONO;
        ctx.lineWidth = 3;
        ctx.strokeStyle = "rgba(7,8,11,0.85)";
        ctx.strokeText(L.text, L.x, cy);
        ctx.fillStyle = rgba(FLAG_RED, 0.8 * fade);
        ctx.fillText(L.text, L.x, cy);
        continue;
      }
      if (L.kind === "plain") {
        const depthFade = s.space === "3d" ? clamp(1.5 - L.depth / (homeW * 1.25), 0.35, 1) : 1;
        ctx.font = L.size + "px " + MONO;
        ctx.lineWidth = 3;
        ctx.strokeStyle = "rgba(7,8,11,0.85)";
        ctx.strokeText(L.text, L.x, cy);
        ctx.fillStyle = rgba(mixRgb(crgb, [1, 1, 1], 0.55), 0.85 * depthFade * fade);
        ctx.fillText(L.text, L.x, cy);
        continue;
      }
      ctx.font = (L.kind === "focus" ? "700 " : "") + L.size + "px " + MONO;
      if (L.kind === "flag") {
        ctx.fillStyle = rgba(FLAG_RED, 0.92 * fade);
        ctx.fillRect(L.x, L.y, L.w, L.h);
        ctx.fillStyle = "#0b0c10";
      } else {
        const col = L.kind === "link" ? LINK_YELLOW : crgb;
        ctx.fillStyle = L.kind === "focus" ? rgba(mixRgb(col, [0, 0, 0], 0.55), 0.92 * fade) : "rgba(8,9,12," + (0.78 * fade).toFixed(3) + ")";
        ctx.fillRect(L.x, L.y, L.w, L.h);
        ctx.strokeStyle = rgba(col, 0.95 * fade);
        ctx.lineWidth = 1;
        ctx.strokeRect(L.x + 0.5, L.y + 0.5, L.w - 1, L.h - 1);
        ctx.fillStyle = L.kind === "focus" ? "#ffffff" : rgba(mixRgb(col, [1, 1, 1], 0.15), fade);
      }
      ctx.fillText(L.text, L.x + 4, cy);
    }
  }

  drawSelection(f, focus) {
    const ctx = this.ctx, app = this.app;
    const ring = (i, dashed, alpha) => {
      const o = i * 3;
      if (i < 0 || f.proj[o + 2] <= 0) return;
      const r = f.radius[i] + 6;
      ctx.save();
      ctx.strokeStyle = rgba(app.nodeColor(i), alpha);
      ctx.lineWidth = 1.5;
      if (dashed) { ctx.setLineDash([4, 4]); ctx.lineDashOffset = -f.time * 14; }
      ctx.beginPath();
      ctx.arc(f.proj[o], f.proj[o + 1], r, 0, TAU);
      ctx.stroke();
      ctx.restore();
    };
    if (app.selected >= 0) ring(app.selected, true, 1);
    if (app.hover >= 0 && app.hover !== app.selected) ring(app.hover, false, 0.7);
  }

  drawSpider(f) {
    const ctx = this.ctx, app = this.app, cr = app.crawler, sp = cr.spider;
    if (!sp.placed) return;
    const t = f.time, d = app.data;
    const core = cr.current >= 0 ? d.clusters[cr.current].rgb : SPIDER_CYAN;
    // silk thread back to the last cluster, or up to the sky while dropping
    ctx.lineWidth = 1;
    if (cr.state === "drop") {
      ctx.strokeStyle = rgba(hexToRgb("#ff4f9a"), 0.7);
      ctx.beginPath();
      ctx.moveTo(sp.x, 0);
      ctx.lineTo(sp.x, sp.y);
      ctx.stroke();
    } else if (cr.silk) {
      const o = cr.silk.node * 3;
      if (f.proj[o + 2] > 0) {
        ctx.strokeStyle = rgba(hexToRgb("#ff4f9a"), 0.65 * cr.silk.life);
        ctx.beginPath();
        ctx.moveTo(f.proj[o], f.proj[o + 1]);
        ctx.lineTo(sp.x, sp.y);
        ctx.stroke();
      }
    }
    cr.drawTentacles(ctx, f.proj, sp.x, sp.y, t, 1);
    sp.draw(ctx, t, core, 1);
  }

  // Burned-in HUD for recorded videos (the DOM dashboard is not captured)
  drawBroadcast(f) {
    const ctx = this.ctx, app = this.app, d = app.data, cr = app.crawler;
    const W = f.w, H = f.h, u = Math.min(W, H) / 54;
    const portrait = H > W * 1.2;
    const pad = u * 2.2;
    ctx.textBaseline = "top";

    ctx.font = "600 " + (u * 0.9).toFixed(1) + "px " + MONO;
    ctx.fillStyle = "rgba(201,209,217,0.7)";
    ctx.fillText("SCIENTOPY · NETWORK CRAWLER · " + d.meta.criterionLabel.toUpperCase(), pad, pad);

    const c = cr.current >= 0 ? d.clusters[cr.current] : null;
    if (c) {
      const ty = pad + u * 2.2;
      ctx.fillStyle = rgba(c.rgb, 1);
      ctx.fillRect(pad, ty, u * 0.3, u * 4.4);
      ctx.font = "700 " + (u * 2.2).toFixed(1) + "px " + MONO;
      ctx.fillStyle = "#f1f5f9";
      const maxChars = Math.floor((W - pad * 3) / (u * 1.35));
      ctx.fillText(truncate(pad2(c.index + 1) + " " + c.label.toUpperCase(), maxChars), pad + u * 1.1, ty);
      ctx.font = (u * 1.05).toFixed(1) + "px " + MONO;
      ctx.fillStyle = rgba(c.rgb, 1);
      ctx.fillText(truncate(c.top.slice(1, 4).join(" · ").toLowerCase(), maxChars + 10), pad + u * 1.1, ty + u * 2.9);
    }

    // log and progress at the bottom
    const lines = app.hud.recentLog(portrait ? 7 : 5);
    const lh = u * 1.35;
    let y = H - pad - u * 3.4 - lines.length * lh;
    ctx.font = (u * 0.95).toFixed(1) + "px " + MONO;
    lines.forEach((L, k) => {
      const a = 0.35 + (0.65 * (k + 1)) / lines.length;
      ctx.fillStyle = "rgba(90,96,108," + a + ")";
      ctx.fillText(L.time, pad, y);
      ctx.fillStyle = L.color.replace("1)", a + ")");
      ctx.fillText(L.verb, pad + u * 3.6, y);
      ctx.fillStyle = "rgba(220,226,232," + a + ")";
      ctx.fillText(truncate(L.text, Math.floor((W - pad * 2 - u * 7.5) / (u * 0.6))), pad + u * 7.2, y);
      y += lh;
    });
    const total = Math.max(1, d.n), frac = cr.readCount / total;
    const by = H - pad - u * 1.2;
    ctx.fillStyle = "rgba(255,255,255,0.1)";
    ctx.fillRect(pad, by, W - pad * 2, u * 0.35);
    ctx.fillStyle = c ? rgba(c.rgb, 1) : "#ff4f9a";
    ctx.fillRect(pad, by, (W - pad * 2) * frac, u * 0.35);
    ctx.font = (u * 0.9).toFixed(1) + "px " + MONO;
    ctx.fillStyle = "rgba(201,209,217,0.85)";
    ctx.fillText("READ " + cr.readCount + "/" + total + "   LINKS " + cr.linkCount + "   FLAGS " + cr.flagged.size + "   CLUSTERS " + d.clusters.length, pad, by - u * 1.5);
    ctx.textAlign = "right";
    ctx.fillStyle = "rgba(255,79,154,0.9)";
    ctx.fillText("scientopy", W - pad, by - u * 1.5);
    ctx.textAlign = "left";
  }
}

function pad2(n) { return n < 10 ? "0" + n : String(n); }

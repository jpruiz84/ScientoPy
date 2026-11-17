/* DOM heads-up display: top stats, cluster tabs, title, dashboard panels,
   node details, tooltip and legend. */

const VERB_COLORS = {
  read: "rgba(255,79,154,1)", link: "rgba(255,209,102,1)", flag: "rgba(255,93,108,1)",
  done: "rgba(75,227,161,1)", walk: "rgba(54,214,231,1)",
};

class Hud {
  constructor(app) {
    this.app = app;
    this.$ = (id) => document.getElementById(id);
    this.log = [];
    this.frame = 0;
    this.codeLines = [];
    this.codeLine = 0;
    this.codeChar = 0;
    this.codeWait = 0;
    this.codeTimes = [];
    this.statT = 0;
    this.scrambleT = 0;
    this.build();
  }

  build() {
    const app = this.app, d = app.data, $ = this.$;
    const meta = d.meta;
    $("st-clusters").textContent = d.clusters.length;
    $("st-nodes").textContent = fmtInt(d.n);
    $("st-source").textContent = (meta.title ? meta.title + " · " : "") + "scientopy." + meta.criterion;
    $("help-meta").textContent = meta.criterionLabel + " · " + meta.startYear + "–" + meta.endYear + " · " +
      fmtInt(meta.papersInRange) + " documents · " + fmtInt(d.n) + " items · " + fmtInt(d.totalLinks) + " links · " +
      meta.counting + " counting · resolution " + meta.resolution + " · generated " + meta.generated + " with ScientoPy " + meta.version;

    // cluster tabs and rows
    const tabs = $("tabs"), list = $("cl-list");
    this.tabEls = [];
    this.rowEls = [];
    d.clusters.forEach((c) => {
      const tab = el("button", { text: c.label, title: c.label + " · " + c.members.length + " items" });
      tab.addEventListener("click", () => app.goToCluster(c.index));
      tabs.appendChild(tab);
      this.tabEls.push(tab);
      const row = el("div", { class: "cl-row", style: "--row-color:" + c.color }, [
        el("div", { class: "cl-top" }, [el("span", { class: "cl-name", text: c.label }), el("span", { class: "cl-n", text: "0/" + c.members.length })]),
        el("div", { class: "cl-bar" }, [el("i")]),
      ]);
      row.addEventListener("click", () => app.goToCluster(c.index));
      list.appendChild(row);
      this.rowEls.push(row);
    });
    $("cl-count").textContent = d.clusters.length;

    // search suggestions
    const dl = $("sp-labels");
    d.nodes.slice().sort((a, b) => b.occ - a.occ).forEach((nd) => dl.appendChild(el("option", { value: nd.label })));

    this.buildRadar();
    this.buildHeat();
    this.updateLegend();
  }

  /* ── events from the crawler ─────────────────────────── */

  onEvent(ev) {
    const d = this.app.data;
    switch (ev.type) {
      case "reset":
        this.log = [];
        this.$("log").innerHTML = "";
        this.$("summary").hidden = true;
        this.refreshClusters();
        this.codeLines = this.makeCode();
        this.codeLine = this.codeChar = 0;
        break;
      case "read":
        this.addLog(ev.t, "read", d.nodes[ev.node].label);
        this.refreshClusters();
        break;
      case "link":
        this.addLog(ev.t, "link", d.nodes[ev.a].label + " · " + d.nodes[ev.b].label);
        break;
      case "flag":
        this.addLog(ev.t, "flag", d.nodes[ev.node].label + " ⚑ " + ev.kind);
        break;
      case "done":
        this.addLog(ev.t, "done", d.clusters[ev.cluster].label.toLowerCase() + " · " + d.clusters[ev.cluster].members.length + " nodes");
        this.refreshClusters();
        break;
      case "walk":
        this.addLog(ev.t, "walk", "→ " + d.clusters[ev.cluster].label.toLowerCase());
        break;
      case "cluster":
        this.setCluster(ev.cluster);
        break;
      case "complete":
        this.showSummary();
        this.refreshClusters();
        break;
    }
  }

  addLog(t, verb, text) {
    const entry = { time: fmtClock(t), verb, text, color: VERB_COLORS[verb] || "rgba(201,209,217,1)" };
    this.log.push(entry);
    if (this.log.length > 60) this.log.shift();
    const ol = this.$("log");
    const li = el("li", null, [
      el("span", { class: "t", text: entry.time }),
      el("span", { class: "v v-" + verb, text: verb }),
      el("span", { class: "w", text }),
    ]);
    ol.appendChild(li);
    while (ol.children.length > 18) ol.removeChild(ol.firstChild);
    const kids = ol.children;
    for (let k = 0; k < kids.length; k++) kids[k].classList.toggle("old", k < kids.length - 9);
  }

  recentLog(k) { return this.log.slice(-k); }

  setCluster(k) {
    const d = this.app.data;
    if (k < 0) return;
    const c = d.clusters[k];
    this.titleTarget = pad2(k + 1);
    this.nameTarget = c.label;
    this.scrambleT = 0.45;
    this.$("titleblock").style.borderLeftColor = c.color;
    const sub = this.$("tb-sub");
    sub.textContent = c.top.slice(1, 5).join(" · ").toLowerCase() || c.members.length + " items";
    sub.style.color = c.color;
    this.refreshClusters();
    this.updateTrend(k);
  }

  refreshClusters() {
    const app = this.app, d = app.data, cr = app.crawler;
    if (!cr) return;
    d.clusters.forEach((c, k) => {
      const status = cr.status[k];
      const tab = this.tabEls[k];
      tab.classList.toggle("active", status === "reading");
      tab.classList.toggle("done", status === "done");
      tab.style.background = status === "reading" ? c.color : "";
      const row = this.rowEls[k];
      row.classList.toggle("active", status === "reading");
      row.classList.toggle("done", status === "done");
      row.querySelector(".cl-n").textContent = cr.clusterRead[k] + "/" + c.members.length;
      const bar = row.querySelector("i");
      bar.style.width = ((100 * cr.clusterRead[k]) / c.members.length).toFixed(1) + "%";
      bar.style.background = status === "reading" ? c.color : status === "done" ? "#e2e8f0" : "#4b5563";
    });
    const activeTab = this.tabEls[cr.current];
    if (activeTab && activeTab.scrollIntoView) activeTab.scrollIntoView({ block: "nearest", inline: "nearest" });
    this.updateRadar();
    this.updateHeat();
  }

  /* ── panels ──────────────────────────────────────────── */

  buildRadar() {
    const d = this.app.data, svg = this.$("radar");
    svg.innerHTML = "";
    const axes = d.clusters.slice(0, 8);
    this.radarAxes = axes;
    const n = Math.max(3, axes.length), cx = 110, cy = 76, R = 56;
    this.radarGeom = { n, cx, cy, R };
    for (const f of [0.25, 0.5, 0.75, 1]) {
      const pts = [];
      for (let k = 0; k < n; k++) {
        const a = -Math.PI / 2 + (TAU * k) / n;
        pts.push((cx + Math.cos(a) * R * f).toFixed(1) + "," + (cy + Math.sin(a) * R * f).toFixed(1));
      }
      svg.appendChild(svgEl("polygon", { class: "ring", points: pts.join(" ") }));
    }
    for (let k = 0; k < n; k++) {
      const a = -Math.PI / 2 + (TAU * k) / n;
      svg.appendChild(svgEl("line", { class: "axis", x1: cx, y1: cy, x2: cx + Math.cos(a) * R, y2: cy + Math.sin(a) * R }));
      const label = svgEl("text", {
        class: "ax-label", x: cx + Math.cos(a) * (R + 11), y: cy + Math.sin(a) * (R + 9) + 3,
        "text-anchor": Math.abs(Math.cos(a)) < 0.2 ? "middle" : Math.cos(a) > 0 ? "start" : "end",
      });
      label.textContent = axes[k] ? axes[k].abbr : "–";
      svg.appendChild(label);
    }
    this.radarShape = svgEl("polygon", { class: "shape", points: "" });
    svg.appendChild(this.radarShape);
  }

  updateRadar() {
    const cr = this.app.crawler, g = this.radarGeom;
    if (!cr || !g) return;
    const pts = [];
    let sum = 0;
    for (let k = 0; k < g.n; k++) {
      const c = this.radarAxes[k];
      const f = c ? cr.clusterRead[c.index] / c.members.length : 0;
      sum += f;
      const a = -Math.PI / 2 + (TAU * k) / g.n, r = g.R * Math.max(0.03, f);
      pts.push((g.cx + Math.cos(a) * r).toFixed(1) + "," + (g.cy + Math.sin(a) * r).toFixed(1));
    }
    this.radarShape.setAttribute("points", pts.join(" "));
    const d = this.app.data;
    this.$("radar-foot").textContent = "coverage " + Math.round((100 * cr.readCount) / Math.max(1, d.n)) + "% · " + cr.linkCount + " links probed";
  }

  buildHeat() {
    const d = this.app.data, heat = this.$("heat");
    heat.innerHTML = "";
    const cols = Math.min(14, d.nYears);
    this.heatYears = d.years.slice(-cols);
    this.heatCells = [];
    d.clusters.slice(0, 7).forEach((c) => {
      const row = el("div", { class: "hr" });
      row.appendChild(el("span", { class: "hl", text: c.abbr }));
      const cells = el("div", { class: "hc", style: "grid-template-columns:repeat(" + cols + ",1fr)" });
      const vals = c.y.slice(-cols), mx = Math.max(1, ...vals);
      const list = [];
      vals.forEach((v, k) => {
        const i = el("i", { title: c.label + " · " + this.heatYears[k] + ": " + v + " docs" });
        cells.appendChild(i);
        list.push([i, v / mx]);
      });
      row.appendChild(cells);
      heat.appendChild(row);
      this.heatCells.push({ c, list });
    });
    this.$("heat-total").textContent = this.heatYears[0] + "–" + this.heatYears[this.heatYears.length - 1];
  }

  updateHeat() {
    const cr = this.app.crawler;
    if (!cr || !this.heatCells) return;
    for (const { c, list } of this.heatCells) {
      const status = cr.status[c.index];
      const lit = status !== "queued" || cr.clusterRead[c.index] > 0;
      for (const [cell, v] of list) {
        cell.style.background = lit ? rgba(c.rgb, 0.12 + 0.88 * v) : "rgba(255,255,255," + (0.04 + 0.1 * v).toFixed(3) + ")";
      }
    }
  }

  updateHeatStats(rate) {
    const cr = this.app.crawler, d = this.app.data;
    this.$("heat-stats").innerHTML =
      '<span class="big">' + rate.toFixed(1) + "<span class=\"dim\" style=\"font-size:10px\"> nodes/s</span></span>" +
      "<span>read</span><b class=\"c-pink\">" + cr.readCount + "</b>" +
      "<span>linked</span><b class=\"c-yellow\">" + cr.linkCount + "</b>" +
      "<span>flagged</span><b class=\"c-red\">" + cr.flagged.size + "</b>" +
      "<span>queued</span><b>" + (d.n - cr.readCount) + "</b>";
  }

  updateTrend(k) {
    const d = this.app.data, c = d.clusters[k];
    const spark = this.$("spark"), gauge = this.$("gauge");
    const ys = c.y, mx = Math.max(1, ...ys), n = ys.length;
    const field = d.docsPerYear, fmx = Math.max(1, ...field);
    const path = (arr, m) => arr.map((v, i) => (i ? "L" : "M") + ((200 * i) / Math.max(1, n - 1)).toFixed(1) + "," + (46 - (40 * v) / m).toFixed(1)).join("");
    spark.innerHTML = "";
    spark.appendChild(svgEl("path", { d: path(field, fmx), fill: "none", stroke: "rgba(255,255,255,0.14)", "stroke-width": 1, "vector-effect": "non-scaling-stroke" }));
    spark.appendChild(svgEl("path", { d: path(ys, mx), fill: "none", stroke: "#ffd166", "stroke-width": 1.6, "vector-effect": "non-scaling-stroke" }));

    const m = c.momentum, cx = 70, cy = 66, R = 46;
    const arc = (from, to) => {
      const a0 = Math.PI + from * Math.PI, a1 = Math.PI + to * Math.PI;
      return "M" + (cx + Math.cos(a0) * R).toFixed(1) + "," + (cy + Math.sin(a0) * R).toFixed(1) +
        "A" + R + "," + R + " 0 0 1 " + (cx + Math.cos(a1) * R).toFixed(1) + "," + (cy + Math.sin(a1) * R).toFixed(1);
    };
    gauge.innerHTML = "";
    gauge.appendChild(svgEl("path", { class: "g-bg", d: arc(0, 1) }));
    if (m > 0) gauge.appendChild(svgEl("path", { class: "g-fg", d: arc(0, Math.max(0.01, m / 100)), stroke: c.color }));
    const tick = svgEl("line", { x1: cx, y1: cy - R - 6, x2: cx, y2: cy - R + 6, stroke: "rgba(255,255,255,0.35)" });
    gauge.appendChild(tick);
    const num = svgEl("text", { class: "g-num", x: cx, y: cy - 6 });
    num.textContent = m;
    gauge.appendChild(num);
    const lab = svgEl("text", { class: "g-lab", x: cx, y: cy + 10 });
    lab.textContent = "momentum · field = 50";
    gauge.appendChild(lab);
    const cr = this.app.crawler;
    this.$("trend-foot").textContent = "avg year " + (c.avgYear ? c.avgYear.toFixed(1) : "–") + " · flags " + (cr ? cr.flagged.size : 0);
  }

  makeCode() {
    const d = this.app.data, meta = d.meta;
    const file = meta.criterion[0].toUpperCase() + meta.criterion.slice(1) + "_network.json";
    const lines = [
      ["c", "# crawler.py · reads a co-occurrence map"],
      ["", 'graph = scientopy.load(<s>"' + file + '"</s>)'],
      ["", "spider = Crawler(legs=<s>8</s>, tentacles=<s>5</s>)"],
      ["", "<k>for</k> cluster <k>in</k> graph.clusters:  <c># " + d.clusters.length + "</c>"],
      ["", "    spider.walk(cluster.hub)"],
      ["", "    spider.read(cluster.nodes)"],
      ["", "    spider.link(top=<s>3</s>)"],
      ["", "    spider.flag(<s>\"emerging\"</s>, <s>\"highly cited\"</s>)"],
    ];
    d.clusters.slice(0, 4).forEach((c) => lines.push(["", "<c># " + escapeHtml(pad2(c.index + 1) + " " + truncate(c.label.toLowerCase(), 26)) + " · " + c.members.length + "</c>"]));
    lines.push(["c", "# reproduce this map:"]);
    (meta.command || "").match(/.{1,38}(\s|$)/g)?.forEach((chunk, k) => lines.push(["c", (k ? "#   " : "# $ ") + escapeHtml(chunk.trim())]));
    // <k>, <s>, <c> are shorthands for the keyword / string / comment spans
    const spans = (html) => html.replace(/<(k|s|c)>/g, '<span class="$1">').replace(/<\/(k|s|c)>/g, "</span>");
    return lines.map(([cls, html]) => spans(cls ? "<" + cls + ">" + html + "</" + cls + ">" : html));
  }

  // Types the code panel one character at a time (tags count as one step)
  tickCode(dt) {
    if (!this.codeLines.length) this.codeLines = this.makeCode();
    const speed = this.app.settings.crawlerPlaying ? this.app.settings.speed : 0.3;
    if (this.codeWait > 0) {
      this.codeWait -= dt;
      if (this.codeWait <= 0) { this.codeLine = 0; this.codeChar = 0; }
      return;
    }
    this.codeAcc = (this.codeAcc || 0) + dt * 38 * speed;
    let changed = false;
    while (this.codeAcc >= 1 && this.codeLine < this.codeLines.length) {
      this.codeAcc -= 1;
      const line = this.codeLines[this.codeLine];
      if (line[this.codeChar] === "<") this.codeChar = line.indexOf(">", this.codeChar) + 1;
      else if (line[this.codeChar] === "&") this.codeChar = line.indexOf(";", this.codeChar) + 1;
      else this.codeChar++;
      if (this.codeChar >= line.length) {
        this.codeLine++;
        this.codeChar = 0;
        this.codeTimes.push(performance.now());
      }
      changed = true;
    }
    if (this.codeLine >= this.codeLines.length) this.codeWait = 4;
    if (!changed) return;
    const done = this.codeLines.slice(0, this.codeLine);
    let partial = "";
    if (this.codeLine < this.codeLines.length) {
      partial = this.codeLines[this.codeLine].slice(0, this.codeChar);
      // close any open span so the partial line stays valid HTML
      const opens = (partial.match(/<span/g) || []).length, closes = (partial.match(/<\/span>/g) || []).length;
      partial += "</span>".repeat(Math.max(0, opens - closes));
    }
    const code = this.$("code");
    code.innerHTML = done.concat([partial + '<span class="cursor"></span>']).join("\n");
    code.scrollTop = code.scrollHeight;
  }

  /* ── per-frame ───────────────────────────────────────── */

  tick(dt) {
    const app = this.app, cr = app.crawler, $ = this.$;
    this.frame++;
    if (this.frame % 2 === 0) $("st-frame").textContent = pad(this.frame % 10000, 4);
    if (this.scrambleT > 0) {
      this.scrambleT -= dt;
      const p = 1 - clamp(this.scrambleT / 0.45, 0, 1);
      $("tb-num").textContent = this.titleTarget;
      $("tb-name").textContent = scramble(this.nameTarget, p);
    }
    this.tickCode(dt);
    this.statT -= dt;
    if (this.statT > 0) return;
    this.statT = 0.12;
    $("st-read").textContent = cr.readCount + "/" + app.data.n;
    $("st-links").textContent = fmtInt(cr.linkCount);
    $("st-flags").textContent = cr.flagged.size;
    $("st-tent").textContent = cr.activeTentacles;
    $("st-time").textContent = cr.elapsed.toFixed(2).padStart(5, "0");
    const rate = cr.readRate();
    $("log-rate").textContent = rate.toFixed(1) + " n/s";
    const now = performance.now();
    while (this.codeTimes.length && now - this.codeTimes[0] > 4000) this.codeTimes.shift();
    $("code-rate").textContent = (this.codeTimes.length / 4).toFixed(1) + " l/s";
    this.updateHeatStats(rate);
  }

  showSummary() {
    const app = this.app, cr = app.crawler, d = app.data;
    const box = this.$("summary");
    box.innerHTML = "";
    box.appendChild(el("h2", { text: "CRAWL COMPLETE" }));
    box.appendChild(el("p", { html: "<b>" + cr.readCount + "/" + d.n + "</b> nodes read · <b class=\"c-yellow\">" + cr.linkCount + "</b> links · <b class=\"c-red\">" + cr.flagged.size + "</b> flags" }));
    box.appendChild(el("p", { class: "dim", text: d.clusters.length + " clusters · " + fmtInt(d.meta.papersInRange) + " documents · " + d.meta.startYear + "–" + d.meta.endYear }));
    const again = el("button", { text: "crawl again" });
    again.addEventListener("click", () => app.restartCrawl());
    const explore = el("button", { text: "explore" });
    explore.addEventListener("click", () => { box.hidden = true; app.setCrawler(false); });
    box.appendChild(el("div", { class: "row" }, [again, explore]));
    box.hidden = false;
    clearTimeout(this.summaryTimer);
    this.summaryTimer = setTimeout(() => { box.hidden = true; }, 8000);
  }

  /* ── node panel, tooltip, legend, toast ──────────────── */

  showNode(i) {
    const app = this.app, d = app.data, nd = d.nodes[i], c = d.clusters[nd.c], meta = d.meta;
    const panel = this.$("nodepanel");
    panel.style.setProperty("--np-color", c.color);
    panel.innerHTML = "";
    const close = el("button", { class: "np-close", title: "Close (Esc)", html: "&times;" });
    close.addEventListener("click", () => app.select(-1));
    panel.appendChild(close);
    const cl = el("div", { class: "np-cluster", text: "cluster " + pad2(c.index + 1) + " · " + c.label, style: "color:" + c.color });
    cl.addEventListener("click", () => app.goToCluster(c.index));
    panel.appendChild(cl);
    panel.appendChild(el("h2", { class: "np-label", text: nd.label }));
    if (nd.flag) panel.appendChild(el("div", { class: "np-flag", text: "⚑ " + nd.flag }));
    const cells = [
      ["occurrences", fmtInt(nd.occ)], ["links", fmtInt(nd.links)], ["link strength", fmtNum(nd.tls)], ["h-index", nd.h],
      ["avg year", nd.avgYear ? nd.avgYear.toFixed(1) : "–"], ["avg cites", fmtNum(nd.avgCit)], ["AGR", fmtNum(nd.agr)], ["PDLY", fmtNum(nd.pdly) + "%"],
    ];
    panel.appendChild(el("div", { class: "np-grid" }, cells.map(([k, v]) => el("div", { html: "<span>" + k + "</span><b>" + escapeHtml(String(v)) + "</b>" }))));

    panel.appendChild(el("div", { class: "np-sec", text: "documents per year · " + meta.startYear + "–" + meta.endYear }));
    const svg = svgEl("svg", { class: "np-years", viewBox: "0 0 " + d.nYears * 10 + " 44", preserveAspectRatio: "none" });
    const mx = Math.max(1, ...nd.y);
    nd.y.forEach((v, k) => {
      const h = (40 * v) / mx;
      const r = svgEl("rect", { x: k * 10 + 1, y: 42 - h, width: 8, height: Math.max(h, v ? 1 : 0.5), fill: v ? c.color : "rgba(255,255,255,0.1)" });
      const tt = svgEl("title", {});
      tt.textContent = d.years[k] + ": " + v;
      r.appendChild(tt);
      svg.appendChild(r);
    });
    panel.appendChild(svg);

    if (d.adj[i].length) {
      panel.appendChild(el("div", { class: "np-sec", text: "strongest links · " + d.adj[i].length }));
      const ol = el("ol", { class: "np-list" });
      const top = d.adj[i].slice(0, 10), wmax = top[0][1];
      for (const [j, w] of top) {
        const li = el("li", null, [
          el("span", { class: "nl-label", text: d.nodes[j].label, style: "color:" + d.clusters[d.nodes[j].c].color }),
          el("span", { class: "nl-bar" }, [el("i", { style: "width:" + ((100 * w) / wmax).toFixed(0) + "%;background:" + d.clusters[d.nodes[j].c].color })]),
          el("span", { class: "nl-w", text: fmtNum(w) }),
        ]);
        li.addEventListener("click", () => app.select(j, true));
        ol.appendChild(li);
      }
      panel.appendChild(ol);
    }

    if (nd.papers && nd.papers.length) {
      panel.appendChild(el("div", { class: "np-sec", text: "most cited documents" }));
      const ol = el("ol", { class: "np-papers" });
      for (const [title, year, cites, doi] of nd.papers) {
        const li = el("li");
        li.appendChild(el("div", { class: "pt", text: title }));
        const m = el("div", { class: "pm", text: year + " · " + fmtInt(cites) + " cites" + (doi ? " · " : "") });
        if (doi) {
          // Opens only when clicked; the map itself makes no network requests
          m.appendChild(el("a", { href: "https://doi.org/" + encodeURI(doi), target: "_blank", rel: "noopener noreferrer", text: doi }));
        }
        li.appendChild(m);
        ol.appendChild(li);
      }
      panel.appendChild(ol);
    }

    panel.appendChild(el("div", { class: "np-sec", text: "analyze in scientopy" }));
    const crit = meta.criterion;
    const cmd = "python scientoPy.py -c " + crit + ' -t "' + nd.label.replace(/"/g, "") + '" --startYear ' + meta.startYear + " --endYear " + meta.endYear;
    const copy = el("button", { text: "copy" });
    copy.addEventListener("click", () => {
      const done = () => this.toast("command copied");
      if (navigator.clipboard) navigator.clipboard.writeText(cmd).then(done, () => this.toast("copy failed: select the text"));
    });
    panel.appendChild(el("div", { class: "np-cmd" }, [el("code", { text: cmd }), copy]));
    panel.hidden = false;
    panel.scrollTop = 0;
  }

  hideNode() { this.$("nodepanel").hidden = true; }

  tooltip(i, x, y) {
    const tt = this.$("tooltip");
    if (i < 0) { tt.hidden = true; return; }
    const d = this.app.data, nd = d.nodes[i], c = d.clusters[nd.c];
    tt.style.setProperty("--tt-color", c.color);
    tt.innerHTML = "<b>" + escapeHtml(nd.label) + "</b>" + fmtInt(nd.occ) + " docs · " + nd.links + " links · avg " +
      (nd.avgYear ? nd.avgYear.toFixed(1) : "–") + (nd.flag ? ' · <span class="c-red">⚑ ' + nd.flag + "</span>" : "");
    tt.hidden = false;
    const w = tt.offsetWidth, h = tt.offsetHeight;
    tt.style.left = Math.min(x + 14, window.innerWidth - w - 8) + "px";
    tt.style.top = Math.max(8, y - h - 10) + "px";
  }

  updateLegend() {
    const d = this.app.data, view = this.app.settings.view, lg = this.$("legend");
    if (view === "network") { lg.hidden = true; return; }
    let title, stops, lo, hi;
    if (view === "year") { title = "avg. publication year"; stops = RAMP_NEON; lo = d.yearLo.toFixed(1); hi = d.yearHi.toFixed(1); }
    else if (view === "cites") { title = "avg. citations (log)"; stops = RAMP_NEON; lo = "0"; hi = "≥ " + fmtNum(d.citesHi); }
    else { title = "item density"; stops = RAMP_INFERNO; lo = "low"; hi = "high"; }
    lg.innerHTML = "<div>" + title + '</div><div class="lg-bar" style="background:' + rampCss(stops) + '"></div><div class="lg-ends"><span>' + lo + "</span><span>" + hi + "</span></div>";
    lg.hidden = false;
  }

  toast(msg, ms) {
    const t = this.$("toast");
    t.textContent = msg;
    t.classList.add("show");
    clearTimeout(this.toastTimer);
    this.toastTimer = setTimeout(() => t.classList.remove("show"), ms || 2200);
  }
}

const SCRAMBLE = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#%&/<>";
function scramble(text, p) {
  const keep = Math.floor(text.length * p);
  let out = text.slice(0, keep);
  for (let k = keep; k < text.length; k++) out += text[k] === " " ? " " : SCRAMBLE[Math.floor(Math.random() * SCRAMBLE.length)];
  return out;
}

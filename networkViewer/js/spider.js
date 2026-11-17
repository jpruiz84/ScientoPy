/* The spider (procedural walking animation, drawn in screen space) and the
   crawler (the tour state machine that walks the map cluster by cluster). */

const SPIDER_CYAN = hexToRgb("#36d6e7");
const LINK_YELLOW = hexToRgb("#ffd166");

// Per side: hip angle on the body, resting foot angle and reach (x R)
const LEG_LAYOUT = [
  { hip: 30, rest: 36, reach: 2.9 },
  { hip: 62, rest: 76, reach: 2.6 },
  { hip: 104, rest: 114, reach: 2.55 },
  { hip: 140, rest: 150, reach: 2.85 },
];

class Spider {
  constructor() {
    this.x = 0; this.y = 0;
    this.vx = 0; this.vy = 0;
    this.heading = -Math.PI / 2;
    this.R = 12;
    this.placed = false;
    this.legs = [];
    for (const side of [-1, 1]) {
      LEG_LAYOUT.forEach((L, k) => {
        this.legs.push({ side, k, L, group: (k + (side > 0 ? 1 : 0)) % 2, foot: [0, 0], from: [0, 0], to: [0, 0], st: 1, stepping: false, lift: 0 });
      });
    }
    this.twitch = 0;
  }

  local(lx, ly) {
    const c = Math.cos(this.heading), s = Math.sin(this.heading);
    return [this.x + c * lx - s * ly, this.y + s * lx + c * ly];
  }

  hip(leg) {
    const a = (leg.side * leg.L.hip * Math.PI) / 180, R = this.R;
    return this.local(0.22 * R + Math.cos(a) * 0.52 * R, Math.sin(a) * 0.46 * R);
  }

  rest(leg) {
    const a = (leg.side * leg.L.rest * Math.PI) / 180, R = this.R;
    return this.local(0.2 * R + Math.cos(a) * leg.L.reach * R, Math.sin(a) * leg.L.reach * R);
  }

  update(dt, x, y, R) {
    this.R = R;
    if (!this.placed) {
      this.x = x; this.y = y; this.placed = true;
      this.legs.forEach((leg) => { leg.foot = this.rest(leg); });
    }
    const idt = 1 / Math.max(dt, 1e-3);
    this.vx = approach(this.vx, (x - this.x) * idt, 10, dt);
    this.vy = approach(this.vy, (y - this.y) * idt, 10, dt);
    this.x = x; this.y = y;
    const speed = Math.hypot(this.vx, this.vy);
    if (speed > 12) this.heading = angleLerp(this.heading, Math.atan2(this.vy, this.vx), 1 - Math.exp(-6 * dt));

    const stepDur = clamp(0.17 - speed * 0.00025, 0.07, 0.17);
    const groupStepping = [false, false];
    this.legs.forEach((leg) => { if (leg.stepping) groupStepping[leg.group] = true; });

    this.twitch -= dt;
    for (const leg of this.legs) {
      if (leg.stepping) {
        leg.st = Math.min(1, leg.st + dt / stepDur);
        const e = easeInOut(leg.st);
        leg.foot = [lerp(leg.from[0], leg.to[0], e), lerp(leg.from[1], leg.to[1], e)];
        leg.lift = Math.sin(Math.PI * leg.st);
        if (leg.st >= 1) { leg.stepping = false; leg.lift = 0; }
        continue;
      }
      const r = this.rest(leg);
      const dist = Math.hypot(leg.foot[0] - r[0], leg.foot[1] - r[1]);
      const other = groupStepping[1 - leg.group];
      if ((dist > R * 0.85 && !other) || dist > R * 3) {
        leg.stepping = true; leg.st = 0;
        leg.from = leg.foot.slice();
        leg.to = [r[0] + this.vx * 0.09, r[1] + this.vy * 0.09];
        groupStepping[leg.group] = true;
      }
    }
    // idle life: a small random step now and then
    if (this.twitch <= 0 && speed < 5) {
      this.twitch = 0.8 + Math.random() * 2.2;
      const leg = this.legs[Math.floor(Math.random() * this.legs.length)];
      if (!leg.stepping) {
        const r = this.rest(leg);
        leg.stepping = true; leg.st = 0; leg.from = leg.foot.slice();
        leg.to = [r[0] + (Math.random() - 0.5) * R * 0.5, r[1] + (Math.random() - 0.5) * R * 0.5];
      }
    }
  }

  knee(hip, foot, leg) {
    const L1 = 1.55 * this.R, L2 = 1.95 * this.R;
    const dx = foot[0] - hip[0], dy = foot[1] - hip[1];
    const d = clamp(Math.hypot(dx, dy), Math.abs(L1 - L2) + 0.01, L1 + L2 - 0.01);
    const a = Math.atan2(dy, dx);
    const th = Math.acos(clamp((L1 * L1 + d * d - L2 * L2) / (2 * L1 * d), -1, 1));
    const k1 = [hip[0] + Math.cos(a + th) * L1, hip[1] + Math.sin(a + th) * L1];
    const k2 = [hip[0] + Math.cos(a - th) * L1, hip[1] + Math.sin(a - th) * L1];
    // knees bend away from the body
    const d1 = Math.hypot(k1[0] - this.x, k1[1] - this.y), d2 = Math.hypot(k2[0] - this.x, k2[1] - this.y);
    const k = d1 > d2 ? k1 : k2;
    if (leg.lift > 0) {
      const ox = k[0] - this.x, oy = k[1] - this.y, ol = Math.hypot(ox, oy) || 1;
      k[0] += (ox / ol) * leg.lift * this.R * 0.45;
      k[1] += (oy / ol) * leg.lift * this.R * 0.45;
    }
    return k;
  }

  draw(ctx, t, coreRgb, alpha) {
    const R = this.R, cyan = rgba(SPIDER_CYAN, 0.9 * alpha), cyanDim = rgba(SPIDER_CYAN, 0.35 * alpha);

    // scanner ring
    ctx.save();
    ctx.strokeStyle = rgba(SPIDER_CYAN, 0.16 * alpha);
    ctx.lineWidth = 1;
    ctx.setLineDash([3, 6]);
    ctx.lineDashOffset = -t * 18;
    ctx.beginPath();
    ctx.arc(this.x, this.y, R * 4.1, 0, TAU);
    ctx.stroke();
    ctx.restore();

    // legs
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    for (const leg of this.legs) {
      const h = this.hip(leg), k = this.knee(h, leg.foot, leg), f = leg.foot;
      ctx.strokeStyle = cyan;
      ctx.lineWidth = Math.max(1, R * 0.11);
      ctx.beginPath();
      ctx.moveTo(h[0], h[1]);
      ctx.lineTo(k[0], k[1]);
      ctx.stroke();
      ctx.lineWidth = Math.max(0.8, R * 0.075);
      ctx.beginPath();
      ctx.moveTo(k[0], k[1]);
      ctx.lineTo(f[0], f[1]);
      ctx.stroke();
      ctx.fillStyle = cyan;
      ctx.beginPath();
      ctx.arc(k[0], k[1], Math.max(1, R * 0.09), 0, TAU);
      ctx.fill();
      ctx.fillStyle = rgba(SPIDER_CYAN, (0.55 + 0.45 * (1 - leg.lift)) * alpha);
      ctx.beginPath();
      ctx.arc(f[0], f[1], Math.max(1, R * 0.08), 0, TAU);
      ctx.fill();
    }

    ctx.save();
    ctx.translate(this.x, this.y);
    ctx.rotate(this.heading);

    // abdomen: meshed sphere seen from above
    const ax = -1.05 * R, rx = 1.18 * R, ry = 0.9 * R;
    ctx.fillStyle = "rgba(6,18,22," + (0.88 * alpha).toFixed(3) + ")";
    ctx.beginPath();
    ctx.ellipse(ax, 0, rx, ry, 0, 0, TAU);
    ctx.fill();
    ctx.save();
    ctx.clip();
    ctx.strokeStyle = cyanDim;
    ctx.lineWidth = 0.7;
    for (let m = 0; m < 6; m++) {
      const ph = t * 0.9 + (m * Math.PI) / 6;
      const w = Math.abs(Math.cos(ph)) * rx;
      ctx.beginPath();
      ctx.ellipse(ax, 0, Math.max(0.5, w), ry, 0, 0, TAU);
      ctx.stroke();
    }
    for (let p = -3; p <= 3; p++) {
      const yy = (p / 4) * ry;
      const half = rx * Math.sqrt(Math.max(0, 1 - (yy * yy) / (ry * ry)));
      ctx.beginPath();
      ctx.moveTo(ax - half, yy);
      ctx.lineTo(ax + half, yy);
      ctx.stroke();
    }
    ctx.restore();
    ctx.strokeStyle = cyan;
    ctx.lineWidth = Math.max(1, R * 0.12);
    ctx.beginPath();
    ctx.ellipse(ax, 0, rx, ry, 0, 0, TAU);
    ctx.stroke();

    // glowing core
    const cs = R * 0.34 * (1 + 0.14 * Math.sin(t * 5));
    ctx.save();
    ctx.shadowColor = rgba(coreRgb, alpha);
    ctx.shadowBlur = R * 1.4;
    ctx.fillStyle = rgba(coreRgb, alpha);
    ctx.beginPath();
    ctx.moveTo(ax + cs, 0);
    ctx.lineTo(ax, cs);
    ctx.lineTo(ax - cs, 0);
    ctx.lineTo(ax, -cs);
    ctx.closePath();
    ctx.fill();
    ctx.restore();

    // cephalothorax, head, eyes and palps
    ctx.fillStyle = "rgba(6,18,22," + (0.92 * alpha).toFixed(3) + ")";
    ctx.strokeStyle = cyan;
    ctx.lineWidth = Math.max(1, R * 0.1);
    ctx.beginPath();
    ctx.ellipse(0.22 * R, 0, 0.6 * R, 0.5 * R, 0, 0, TAU);
    ctx.fill();
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(0.98 * R, 0, 0.3 * R, 0, TAU);
    ctx.fill();
    ctx.stroke();
    ctx.fillStyle = rgba([1, 1, 1], 0.9 * alpha);
    for (const s of [-1, 1]) {
      ctx.beginPath();
      ctx.arc(1.1 * R, s * 0.11 * R, Math.max(0.8, 0.065 * R), 0, TAU);
      ctx.fill();
    }
    ctx.lineWidth = Math.max(0.8, R * 0.07);
    for (const s of [-1, 1]) {
      const wig = Math.sin(t * 6 + s) * 0.08 * R;
      ctx.beginPath();
      ctx.moveTo(1.2 * R, s * 0.16 * R);
      ctx.quadraticCurveTo(1.45 * R, s * (0.3 * R) + wig, 1.6 * R, s * 0.18 * R + wig);
      ctx.stroke();
    }
    ctx.restore();
  }
}

/* ── Crawler: the tour ─────────────────────────────────────── */

const TENT_EXTEND = 0.22, TENT_HOLD = 0.55, TENT_RETRACT = 0.25;

class Crawler {
  constructor(app) {
    this.app = app;
    this.spider = new Spider();
    this.tmpA = [0, 0, 0];
    this.tmpB = [0, 0, 0];
    this.reset();
  }

  reset() {
    const d = this.app.data;
    this.read = new Uint8Array(d.n);
    this.readCount = 0;
    this.linkedPairs = new Set();
    this.linkCount = 0;
    this.flagged = new Map();
    this.clusterRead = new Int32Array(d.clusters.length);
    this.status = d.clusters.map(() => "queued");
    this.order = d.clusters.map((c) => c.index);
    this.step = 0;
    this.state = d.n ? "drop" : "idle";
    this.stateT = 0;
    this.from = this.to = d.n ? d.clusters[0].hub : -1;
    this.travelT = 1;
    this.travelDur = 1;
    this.tentacles = [];
    this.elapsed = 0;
    this.silk = null;
    this.readTimes = [];
    this.spider.placed = false;
    if (d.clusters.length) this.status[0] = "reading";
    this.emit({ type: "reset" });
    this.emit({ type: "cluster", cluster: this.current });
  }

  get current() { return this.order[this.step] != null ? this.order[this.step] : -1; }
  get activeTentacles() { return this.tentacles.filter((tn) => tn.age >= tn.delay).length; }

  emit(ev) {
    ev.t = this.elapsed;
    if (this.app.hud) this.app.hud.onEvent(ev);
  }

  position(out) {
    if (this.to < 0) { out[0] = out[1] = out[2] = 0; return out; }
    this.app.worldPos(this.to, this.tmpB);
    if (this.state === "travel") {
      this.app.worldPos(this.from, this.tmpA);
      const e = easeInOut(clamp(this.travelT, 0, 1));
      for (let k = 0; k < 3; k++) out[k] = lerp(this.tmpA[k], this.tmpB[k], e);
    } else {
      out[0] = this.tmpB[0]; out[1] = this.tmpB[1]; out[2] = this.tmpB[2];
    }
    return out;
  }

  // 0..1 while the spider drops in on its thread
  get dropProgress() {
    return this.state === "drop" ? easeOut(clamp(this.stateT / 1.5, 0, 1)) : 1;
  }

  update(dt) {
    if (this.state === "idle") return;
    this.elapsed += dt;
    this.stateT += dt;
    this.updateTentacles(dt);
    if (this.silk) {
      this.silk.life -= dt * (this.state === "travel" ? 0.15 : 0.6);
      if (this.silk.life <= 0) this.silk = null;
    }

    switch (this.state) {
      case "drop":
        if (this.stateT > 1.6) this.arrive(this.to);
        break;
      case "travel":
        this.travelT += dt / this.travelDur;
        if (this.travelT >= 1) { this.travelT = 1; this.arrive(this.to); }
        break;
      case "probe":
        if (this.stateT > 0.8 && !this.tentacles.some((tn) => !tn.fired)) this.next();
        break;
      case "complete":
        if (this.stateT > 10 && this.app.settings.loop) this.reset();
        break;
    }
  }

  updateTentacles(dt) {
    for (const tn of this.tentacles) {
      tn.age += dt;
      if (!tn.fired && tn.age >= tn.delay + TENT_EXTEND) {
        tn.fired = true;
        if (tn.kind === "read") this.readNode(tn.node);
        else this.linkPair(tn.origin, tn.node, tn.w);
      }
    }
    this.tentacles = this.tentacles.filter((tn) => tn.age < tn.delay + TENT_EXTEND + TENT_HOLD + TENT_RETRACT);
  }

  arrive(i) {
    const d = this.app.data;
    this.state = "probe";
    this.stateT = 0;
    this.readNode(i);
    const c = d.nodes[i].c;
    const here = this.app.worldPos(i, [0, 0, 0]);
    const tmp = [0, 0, 0];
    const near = d.clusters[c].members
      .filter((j) => !this.read[j] && j !== i)
      .map((j) => { this.app.worldPos(j, tmp); return [j, Math.hypot(tmp[0] - here[0], tmp[1] - here[1], tmp[2] - here[2])]; })
      .sort((a, b) => a[1] - b[1])
      .slice(0, 5);
    near.forEach(([j], k) => this.tentacles.push({ kind: "read", node: j, origin: i, delay: k * 0.07, age: 0, fired: false }));
    let probes = 0;
    for (const [j, w] of d.adj[i]) {
      if (probes >= 3) break;
      const key = i < j ? i + ":" + j : j + ":" + i;
      if (this.linkedPairs.has(key)) continue;
      this.tentacles.push({ kind: "link", node: j, origin: i, w, delay: 0.15 + probes * 0.1, age: 0, fired: false });
      probes++;
    }
  }

  next() {
    const d = this.app.data, c = this.current;
    const remaining = c >= 0 ? d.clusters[c].members.filter((j) => !this.read[j]) : [];
    if (remaining.length) {
      const here = this.app.worldPos(this.to, [0, 0, 0]), tmp = [0, 0, 0];
      const maxOcc = d.nodes[d.clusters[c].hub].occ;
      let best = remaining[0], bestScore = Infinity;
      for (const j of remaining) {
        this.app.worldPos(j, tmp);
        const dist = Math.hypot(tmp[0] - here[0], tmp[1] - here[1], tmp[2] - here[2]);
        const score = dist / (0.6 + Math.sqrt(d.nodes[j].occ / maxOcc));
        if (score < bestScore) { bestScore = score; best = j; }
      }
      this.travelTo(best);
      return;
    }
    this.finishCluster();
  }

  finishCluster() {
    const d = this.app.data, c = this.current;
    if (c >= 0) {
      this.status[c] = "done";
      this.emit({ type: "done", cluster: c });
    }
    let s = this.step + 1;
    while (s < this.order.length && this.status[this.order[s]] === "done") s++;
    if (s >= this.order.length) {
      // pick up clusters skipped by jumping around
      s = this.order.findIndex((k) => this.status[k] !== "done");
    }
    if (s < 0 || s >= this.order.length) {
      this.state = "complete";
      this.stateT = 0;
      this.emit({ type: "complete" });
      return;
    }
    this.step = s;
    const k = this.current;
    this.status[k] = "reading";
    this.silk = { node: this.to, life: 1 };
    this.emit({ type: "cluster", cluster: k });
    this.emit({ type: "walk", cluster: k });
    const target = d.clusters[k].members.find((j) => !this.read[j]);
    this.travelTo(target != null ? target : d.clusters[k].hub);
  }

  travelTo(j) {
    const a = this.app.worldPos(this.to, [0, 0, 0]), b = this.app.worldPos(j, [0, 0, 0]);
    const dist = Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
    this.from = this.to;
    this.to = j;
    this.travelT = 0;
    this.travelDur = clamp(dist / 80, 0.3, 2.8);
    this.state = "travel";
    this.stateT = 0;
  }

  jumpTo(k) {
    if (k === this.current && this.state !== "complete") return;
    const d = this.app.data, prev = this.current;
    if (prev >= 0 && this.status[prev] === "reading") {
      this.status[prev] = this.clusterRead[prev] >= d.clusters[prev].members.length ? "done" : "queued";
    }
    this.step = this.order.indexOf(k);
    this.status[k] = "reading";
    this.tentacles = this.tentacles.filter((tn) => tn.fired);
    this.silk = { node: this.to, life: 1 };
    this.emit({ type: "cluster", cluster: k });
    this.emit({ type: "walk", cluster: k });
    const target = d.clusters[k].members.find((j) => !this.read[j]);
    this.travelTo(target != null ? target : d.clusters[k].hub);
  }

  readNode(i) {
    if (this.read[i]) return;
    const nd = this.app.data.nodes[i];
    this.read[i] = 1;
    this.readCount++;
    this.clusterRead[nd.c]++;
    this.readTimes.push(this.elapsed);
    this.emit({ type: "read", node: i });
    if (nd.flag && !this.flagged.has(i)) {
      this.flagged.set(i, nd.flag);
      this.emit({ type: "flag", node: i, kind: nd.flag });
    }
  }

  linkPair(i, j, w) {
    const key = i < j ? i + ":" + j : j + ":" + i;
    if (this.linkedPairs.has(key)) return;
    this.linkedPairs.add(key);
    this.linkCount++;
    this.emit({ type: "link", a: i, b: j, w });
  }

  readRate() {
    const now = this.elapsed;
    while (this.readTimes.length && now - this.readTimes[0] > 3) this.readTimes.shift();
    return this.readTimes.length / 3;
  }

  // Tentacles and threads, drawn under the spider
  drawTentacles(ctx, proj, sx, sy, t, alpha) {
    const d = this.app.data;
    for (const tn of this.tentacles) {
      const age = tn.age - tn.delay;
      if (age < 0) continue;
      let ext = clamp(age / TENT_EXTEND, 0, 1);
      const back = age - TENT_EXTEND - TENT_HOLD;
      if (back > 0) ext = 1 - clamp(back / TENT_RETRACT, 0, 1);
      const o = tn.node * 3;
      if (proj[o + 2] <= 0) continue;
      const tx = proj[o], ty = proj[o + 1];
      const dx = tx - sx, dy = ty - sy, len = Math.hypot(dx, dy) || 1;
      const bend = Math.sin(t * 3 + tn.node) * len * 0.12;
      const cx = sx + dx / 2 - (dy / len) * bend, cy = sy + dy / 2 + (dx / len) * bend;
      const col = tn.kind === "link" ? LINK_YELLOW : d.clusters[d.nodes[tn.node].c].rgb;
      ctx.strokeStyle = rgba(col, 0.75 * alpha);
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(sx, sy);
      const steps = 14;
      let px = sx, py = sy;
      for (let s = 1; s <= steps; s++) {
        const u = (s / steps) * ext, iu = 1 - u;
        px = iu * iu * sx + 2 * iu * u * cx + u * u * tx;
        py = iu * iu * sy + 2 * iu * u * cy + u * u * ty;
        ctx.lineTo(px, py);
      }
      ctx.stroke();
      ctx.fillStyle = rgba(col, alpha);
      ctx.beginPath();
      ctx.arc(px, py, 2.2, 0, TAU);
      ctx.fill();
      if (ext >= 1 && back <= 0) {
        // data pulse travelling back to the spider
        const u = 1 - ((age - TENT_EXTEND) / TENT_HOLD) % 1, iu = 1 - u;
        const qx = iu * iu * sx + 2 * iu * u * cx + u * u * tx, qy = iu * iu * sy + 2 * iu * u * cy + u * u * ty;
        ctx.fillStyle = rgba([1, 1, 1], 0.9 * alpha);
        ctx.beginPath();
        ctx.arc(qx, qy, 1.6, 0, TAU);
        ctx.fill();
      }
    }
  }
}

/* Orbit camera with smoothed motion and a vertical lens shift that keeps the
   map centered in the area left free by the HUD. */

class Camera {
  constructor() {
    this.fov = (42 * Math.PI) / 180;
    this.cur = { yaw: 0.55, pitch: 0.2, dist: 320, tx: 0, ty: 0, tz: 0 };
    this.goal = Object.assign({}, this.cur);
    this.rate = 3;
    this.homeDist = 300;
    this.view = new Float32Array(16);
    this.proj = new Float32Array(16);
    this.vp = new Float32Array(16);
    this.eye = [0, 0, 0];
    this.w = 1; this.h = 1;
    this.shiftY = 0; this.shiftX = 0;
    this.availW = 1; this.availH = 1;
  }

  setViewport(w, h, pads) {
    this.w = w; this.h = h;
    const top = pads.top, bottom = pads.bottom, left = pads.left || 0, right = pads.right || 0;
    this.availH = Math.max(80, h - top - bottom);
    this.availW = Math.max(80, w - left - right);
    const cy = top + this.availH / 2, cx = left + this.availW / 2;
    this.shiftY = (h / 2 - cy) / (h / 2);
    this.shiftX = (cx - w / 2) / (w / 2);
  }

  // Distance that fits a sphere of the given radius in the free area
  fitDistance(radius) {
    const t = Math.tan(this.fov / 2);
    const fracH = this.availH / this.h, fracW = (this.availW / this.w) * (this.w / this.h);
    return (radius * 1.08) / (t * Math.min(fracH, fracW));
  }

  update(dt, flat) {
    const c = this.cur, g = this.goal, r = this.rate;
    if (flat) {
      g.pitch = 0;
      g.yaw = Math.round(g.yaw / TAU) * TAU;
    }
    c.yaw = approach(c.yaw, g.yaw, r, dt);
    c.pitch = approach(c.pitch, g.pitch, r, dt);
    c.dist = approach(c.dist, g.dist, r, dt);
    c.tx = approach(c.tx, g.tx, r, dt);
    c.ty = approach(c.ty, g.ty, r, dt);
    c.tz = approach(c.tz, g.tz, r, dt);
    this.computeMatrices();
  }

  computeMatrices() {
    const c = this.cur;
    const cp = Math.cos(c.pitch);
    this.eye[0] = c.tx + c.dist * cp * Math.sin(c.yaw);
    this.eye[1] = c.ty + c.dist * Math.sin(c.pitch);
    this.eye[2] = c.tz + c.dist * cp * Math.cos(c.yaw);
    Mat4.lookAt(this.view, this.eye, [c.tx, c.ty, c.tz], [0, 1, 0]);
    Mat4.perspective(this.proj, this.fov, this.w / this.h, Math.max(0.5, c.dist * 0.02), c.dist * 6 + 800);
    // lens shift: x_ndc += shiftX, y_ndc += shiftY (clip.w = -z_eye)
    this.proj[8] -= this.shiftX;
    this.proj[9] -= this.shiftY;
    Mat4.multiply(this.vp, this.proj, this.view);
  }

  // World -> CSS pixels. Writes [x, y, w] into out at offset o; w <= 0 is behind.
  project(x, y, z, out, o) {
    const m = this.vp;
    const cx = m[0] * x + m[4] * y + m[8] * z + m[12];
    const cy = m[1] * x + m[5] * y + m[9] * z + m[13];
    const cw = m[3] * x + m[7] * y + m[11] * z + m[15];
    const iw = cw > 1e-6 ? 1 / cw : 0;
    out[o] = (cx * iw * 0.5 + 0.5) * this.w;
    out[o + 1] = (0.5 - cy * iw * 0.5) * this.h;
    out[o + 2] = cw;
  }

  // Pixels per world unit at clip depth w
  pixelScale(w) {
    return this.h / (2 * Math.tan(this.fov / 2) * Math.max(w, 1e-3));
  }

  orbit(dx, dy) {
    this.rate = 14;
    this.goal.yaw -= dx * 0.0055;
    this.goal.pitch = clamp(this.goal.pitch + dy * 0.0055, -1.45, 1.45);
  }

  pan(dx, dy) {
    this.rate = 14;
    const wpp = (2 * this.cur.dist * Math.tan(this.fov / 2)) / this.h;
    const v = this.view;
    this.goal.tx += (-v[0] * dx + v[1] * dy) * wpp;
    this.goal.ty += (-v[4] * dx + v[5] * dy) * wpp;
    this.goal.tz += (-v[8] * dx + v[9] * dy) * wpp;
  }

  zoom(factor) {
    this.rate = Math.max(this.rate, 8);
    this.goal.dist = clamp(this.goal.dist * factor, 18, this.homeDist * 5);
  }

  flyTo(x, y, z, dist, rate) {
    this.rate = rate || 2.6;
    this.goal.tx = x; this.goal.ty = y; this.goal.tz = z;
    if (dist) this.goal.dist = dist;
  }
}

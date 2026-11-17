/* WebGL2 renderer: particle nebulae, links, glowing nodes and the density map.

   Per-node state lives in a float texture (one column per node) that every
   shader samples with texelFetch:
     row 0: x3, y3, z3, size (css px)
     row 1: x2, y2, intro delay, -
     row 2: r, g, b, -
     row 3: visibility, emphasis, highlight, read
   so particles, links and nodes all follow the crawler, timeline and hover
   state without rebuilding any vertex buffer. */

const GLSL_HEAD = `#version 300 es
precision highp float;
precision highp int;
precision highp sampler2D;
uniform sampler2D u_nodes;
uniform mat4 u_vp;
uniform float u_morph, u_time, u_scale, u_pr, u_intro, u_focal;
vec4 nodeRow(int i, int row) { return texelFetch(u_nodes, ivec2(i, row), 0); }
vec3 nodePos(int i) {
  vec4 r1 = nodeRow(i, 1);
  return mix(nodeRow(i, 0).xyz, vec3(r1.xy, 0.0), u_morph);
}
float introAt(float delay) {
  float t = clamp((u_intro - delay) / 0.9, 0.0, 1.0);
  return 1.0 - pow(1.0 - t, 3.0);
}
vec3 introSpin(vec3 p, float e) {
  float a = (1.0 - e) * 2.4;
  float c = cos(a), s = sin(a);
  return vec3(c * p.x - s * p.z, p.y, s * p.x + c * p.z) * e;
}
`;

const VS_PARTICLES = GLSL_HEAD + `
layout(location = 0) in vec4 a_part;   // node a, node b, t along the link, seed
layout(location = 1) in vec3 a_off;
uniform float u_size, u_alpha, u_hlActive;
out vec4 v_col;
void main() {
  int ia = int(a_part.x + 0.5), ib = int(a_part.y + 0.5);
  float t = a_part.z, seed = a_part.w;
  vec3 base = mix(nodePos(ia), nodePos(ib), t);
  vec3 off = a_off;
  off.z *= mix(1.0, 0.18, u_morph);
  float ph = seed * 6.2831853;
  off *= 1.0 + 0.07 * sin(u_time * (0.35 + seed * 0.6) + ph);
  off += 0.0035 * vec3(sin(u_time * 0.9 + ph * 3.0), cos(u_time * 0.7 + ph * 5.0), sin(u_time * 0.5 + ph * 7.0));
  float e = introAt(nodeRow(ia, 1).z + seed * 0.3);
  vec3 p = introSpin((base + off) * u_scale, e);
  vec4 clip = u_vp * vec4(p, 1.0);
  gl_Position = clip;
  float persp = clamp(u_focal / max(clip.w, 1.0), 0.4, 4.0);
  gl_PointSize = u_size * (0.55 + 0.9 * fract(seed * 13.37)) * u_pr * persp;
  vec4 sa = nodeRow(ia, 3), sb = nodeRow(ib, 3);
  float vis = mix(sa.x, sb.x, t);
  float emph = mix(sa.y, sb.y, t);
  float hl = max(sa.z, sb.z);
  vec3 col = mix(nodeRow(ia, 2).rgb, nodeRow(ib, 2).rgb, t);
  float a = u_alpha * vis * emph * e * (0.45 + 0.55 * fract(seed * 7.13));
  a *= 0.78 + 0.22 * sin(u_time * (0.8 + seed * 2.5) + ph * 11.0);
  a *= (u_hlActive > 0.5) ? (0.35 + 1.6 * hl) : 1.0;
  a *= 1.0 + 0.6 * max(sa.w, sb.w);
  v_col = vec4(col * a, a);
}`;

const FS_PARTICLES = `#version 300 es
precision mediump float;
in vec4 v_col;
out vec4 o;
void main() {
  vec2 d = gl_PointCoord - 0.5;
  float r = dot(d, d) * 4.0;
  if (r > 1.0) discard;
  o = v_col * exp(-r * 3.2);
}`;

const VS_NODES = GLSL_HEAD + `
layout(location = 0) in float a_idx;
uniform float u_nodeScale, u_hlActive;
out vec4 v_col;
out float v_read;
void main() {
  int i = int(a_idx + 0.5);
  vec4 r0 = nodeRow(i, 0);
  vec4 st = nodeRow(i, 3);
  float e = introAt(nodeRow(i, 1).z + 0.15);
  vec3 p = introSpin(nodePos(i) * u_scale, e);
  vec4 clip = u_vp * vec4(p, 1.0);
  gl_Position = clip;
  float persp = clamp(u_focal / max(clip.w, 1.0), 0.35, 3.5);
  gl_PointSize = r0.w * 2.0 * u_nodeScale * u_pr * persp * st.x * e * (1.0 + 0.35 * step(0.99, st.z));
  float dim = (u_hlActive > 0.5 && st.z < 0.25) ? 0.3 : 1.0;
  v_col = vec4(nodeRow(i, 2).rgb, st.y * dim);
  v_read = st.w;
}`;

const FS_NODES = `#version 300 es
precision mediump float;
in vec4 v_col;
in float v_read;
out vec4 o;
void main() {
  vec2 d = gl_PointCoord - 0.5;
  float r = length(d) * 2.0;
  if (r > 1.0) discard;
  float core = smoothstep(0.5, 0.36, r);
  float rim = smoothstep(0.62, 0.52, r) * smoothstep(0.38, 0.5, r);
  float glow = exp(-r * r * 4.5);
  vec3 c = v_col.rgb;
  vec3 col = c * glow * 0.55 + mix(c, vec3(1.0), 0.25 + 0.35 * v_read) * core * 0.85 + c * rim * 0.6;
  o = vec4(col * v_col.a, 1.0);
}`;

const VS_EDGES = GLSL_HEAD + `
layout(location = 0) in vec4 a_e;   // this end, other end, weight 0..1, rank
uniform float u_maxRank, u_edgeAlpha, u_hlActive;
out vec4 v_col;
void main() {
  int i = int(a_e.x + 0.5), j = int(a_e.y + 0.5);
  float e = min(introAt(nodeRow(i, 1).z + 0.25), introAt(nodeRow(j, 1).z + 0.25));
  vec3 p = introSpin(nodePos(i) * u_scale, e);
  gl_Position = u_vp * vec4(p, 1.0);
  vec4 si = nodeRow(i, 3), sj = nodeRow(j, 3);
  float vis = min(si.x, sj.x) * e;
  float focus = step(0.99, max(si.z, sj.z));
  float show = a_e.w < u_maxRank ? 1.0 : 0.0;
  float a = u_edgeAlpha * (0.18 + 0.82 * a_e.z) * show * 0.5 * (si.y + sj.y);
  if (u_hlActive > 0.5) a = focus > 0.5 ? 0.25 + 0.6 * a_e.z : a * 0.22;
  a *= vis;
  v_col = vec4(nodeRow(i, 2).rgb * a, a);
}`;

const FS_FLAT = `#version 300 es
precision mediump float;
in vec4 v_col;
out vec4 o;
void main() { o = v_col; }`;

const VS_SPLAT = GLSL_HEAD + `
layout(location = 0) in float a_idx;
uniform float u_kernel, u_focalPx, u_splatScale;
out float v_w;
void main() {
  int i = int(a_idx + 0.5);
  vec4 st = nodeRow(i, 3);
  float e = introAt(nodeRow(i, 1).z + 0.15);
  vec3 p = introSpin(nodePos(i) * u_scale, e);
  vec4 clip = u_vp * vec4(p, 1.0);
  gl_Position = clip;
  gl_PointSize = min(2.0 * u_kernel * u_scale * u_focalPx / max(clip.w, 1.0), 1024.0);
  v_w = (0.12 + nodeRow(i, 0).w / 34.0) * st.x * e * u_splatScale;
}`;

const FS_SPLAT = `#version 300 es
precision highp float;
in float v_w;
out vec4 o;
void main() {
  vec2 d = gl_PointCoord - 0.5;
  float r = dot(d, d) * 4.0;
  if (r > 1.0) discard;
  o = vec4(v_w * exp(-r * 3.0) * (1.0 - r), 0.0, 0.0, 1.0);
}`;

const VS_FULL = `#version 300 es
out vec2 v_uv;
void main() {
  vec2 p = vec2(float((gl_VertexID << 1) & 2), float(gl_VertexID & 2));
  v_uv = p;
  gl_Position = vec4(p * 2.0 - 1.0, 0.0, 1.0);
}`;

const FS_DENSITY = `#version 300 es
precision highp float;
uniform sampler2D u_dens;
uniform sampler2D u_lut;
uniform float u_gain;
uniform vec3 u_bg;
in vec2 v_uv;
out vec4 o;
void main() {
  float d = texture(u_dens, v_uv).r;
  float v = 1.0 - exp(-d * u_gain);
  vec3 c = texture(u_lut, vec2(clamp(0.04 + v * 0.95, 0.0, 1.0), 0.5)).rgb;
  o = vec4(mix(u_bg, c, smoothstep(0.0, 0.1, v)), 1.0);
}`;

class Renderer {
  constructor(canvas, data) {
    const gl = canvas.getContext("webgl2", { antialias: true, alpha: false, premultipliedAlpha: false, preserveDrawingBuffer: false, powerPreference: "high-performance" });
    if (!gl) throw new Error("WebGL2 is not available in this browser.");
    this.gl = gl;
    this.canvas = canvas;
    this.data = data;
    this.floatFbo = !!gl.getExtension("EXT_color_buffer_float");
    this.bg = hexToRgb("#07080b");

    this.progParticles = this.program(VS_PARTICLES, FS_PARTICLES);
    this.progNodes = this.program(VS_NODES, FS_NODES);
    this.progEdges = this.program(VS_EDGES, FS_FLAT);
    this.progSplat = this.program(VS_SPLAT, FS_SPLAT);
    this.progDensity = this.program(VS_FULL, FS_DENSITY);

    this.n = data.n;
    this.texW = Math.max(1, this.n);
    this.nodeData = new Float32Array(this.texW * 4 * 4);
    this.nodeTex = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, this.nodeTex);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA32F, this.texW, 4, 0, gl.RGBA, gl.FLOAT, null);
    this.initNodeRows();

    this.lutTex = this.makeLut(RAMP_INFERNO);
    this.buildNodeBuffer();
    this.buildEdgeBuffer();
    this.buildParticles();
    this.emptyVao = gl.createVertexArray();
    this.fbo = null;
    this.fboW = 0; this.fboH = 0;
  }

  program(vsSrc, fsSrc) {
    const gl = this.gl;
    const compile = (type, src) => {
      const s = gl.createShader(type);
      gl.shaderSource(s, src);
      gl.compileShader(s);
      if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error("Shader error: " + gl.getShaderInfoLog(s));
      return s;
    };
    const p = gl.createProgram();
    gl.attachShader(p, compile(gl.VERTEX_SHADER, vsSrc));
    gl.attachShader(p, compile(gl.FRAGMENT_SHADER, fsSrc));
    gl.linkProgram(p);
    if (!gl.getProgramParameter(p, gl.LINK_STATUS)) throw new Error("Program error: " + gl.getProgramInfoLog(p));
    const uniforms = {};
    const count = gl.getProgramParameter(p, gl.ACTIVE_UNIFORMS);
    for (let k = 0; k < count; k++) {
      const info = gl.getActiveUniform(p, k);
      uniforms[info.name] = gl.getUniformLocation(p, info.name);
    }
    return { p, u: uniforms };
  }

  makeLut(stops) {
    const gl = this.gl;
    const px = new Uint8Array(256 * 4);
    for (let k = 0; k < 256; k++) {
      const c = ramp(stops, k / 255);
      px[k * 4] = c[0] * 255; px[k * 4 + 1] = c[1] * 255; px[k * 4 + 2] = c[2] * 255; px[k * 4 + 3] = 255;
    }
    const tex = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, tex);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA8, 256, 1, 0, gl.RGBA, gl.UNSIGNED_BYTE, px);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    return tex;
  }

  initNodeRows() {
    const d = this.data, W = this.texW, nd = this.nodeData;
    d.nodes.forEach((node, i) => {
      const r0 = i * 4, r1 = (W + i) * 4;
      nd[r0] = node.p3[0]; nd[r0 + 1] = node.p3[1]; nd[r0 + 2] = node.p3[2];
      nd[r1] = node.p2[0]; nd[r1 + 1] = node.p2[1];
      // big bang: larger clusters unfold first
      nd[r1 + 2] = Math.min(0.5, (node.c / Math.max(1, d.clusters.length)) * 0.45 + ((i * 0.618) % 1) * 0.05);
    });
  }

  // sizes/colors/states: Float32Array(n), Float32Array(n*3), Float32Array(n*4)
  updateNodes(sizes, colors, states) {
    const gl = this.gl, W = this.texW, nd = this.nodeData, n = this.n;
    for (let i = 0; i < n; i++) {
      nd[i * 4 + 3] = sizes[i];
      const r2 = (2 * W + i) * 4, r3 = (3 * W + i) * 4;
      nd[r2] = colors[i * 3]; nd[r2 + 1] = colors[i * 3 + 1]; nd[r2 + 2] = colors[i * 3 + 2];
      nd[r3] = states[i * 4]; nd[r3 + 1] = states[i * 4 + 1]; nd[r3 + 2] = states[i * 4 + 2]; nd[r3 + 3] = states[i * 4 + 3];
    }
    gl.bindTexture(gl.TEXTURE_2D, this.nodeTex);
    gl.texSubImage2D(gl.TEXTURE_2D, 0, 0, 0, W, 4, gl.RGBA, gl.FLOAT, nd);
  }

  vao(setup) {
    const gl = this.gl;
    const v = gl.createVertexArray();
    gl.bindVertexArray(v);
    setup(gl);
    gl.bindVertexArray(null);
    return v;
  }

  buildNodeBuffer() {
    const idx = new Float32Array(this.n);
    for (let i = 0; i < this.n; i++) idx[i] = i;
    this.nodeVao = this.vao((gl) => {
      gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer());
      gl.bufferData(gl.ARRAY_BUFFER, idx, gl.STATIC_DRAW);
      gl.enableVertexAttribArray(0);
      gl.vertexAttribPointer(0, 1, gl.FLOAT, false, 4, 0);
    });
  }

  buildEdgeBuffer() {
    const links = this.data.links, maxW = this.data.max.weight;
    const buf = new Float32Array(links.length * 8);
    links.forEach(([i, j, w], k) => {
      const wn = Math.sqrt(w / maxW);
      buf.set([i, j, wn, k, j, i, wn, k], k * 8);
    });
    this.edgeCount = links.length * 2;
    this.edgeVao = this.vao((gl) => {
      gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer());
      gl.bufferData(gl.ARRAY_BUFFER, buf, gl.STATIC_DRAW);
      gl.enableVertexAttribArray(0);
      gl.vertexAttribPointer(0, 4, gl.FLOAT, false, 16, 0);
    });
  }

  buildParticles() {
    const d = this.data, rand = mulberry32(20260406);
    const budget = clamp(40000 + d.n * 180, 40000, 120000);
    const parts = [];
    const push = (a, b, t, ox, oy, oz) => parts.push(a, b, t, rand(), ox, oy, oz);
    const sphere = (sigma) => {
      const r = Math.abs(gaussian(rand)) * sigma;
      const u = rand() * 2 - 1, th = rand() * TAU, s = Math.sqrt(1 - u * u);
      return [r * s * Math.cos(th), r * s * Math.sin(th), r * u];
    };

    // Clouds around every node
    const wsum = d.nodes.reduce((acc, nd) => acc + Math.sqrt(nd.occ) + 0.5, 0);
    d.nodes.forEach((nd, i) => {
      const count = Math.max(10, Math.round((budget * 0.6 * (Math.sqrt(nd.occ) + 0.5)) / wsum));
      const sigma = 0.028 + 0.06 * Math.sqrt(nd.occ / d.max.occ);
      for (let k = 0; k < count; k++) {
        const o = sphere(rand() < 0.72 ? sigma : sigma * 2.5);
        push(i, i, 0, o[0], o[1], o[2]);
      }
    });

    // Filaments along the strongest links
    const top = d.links.slice(0, 3200);
    const lsum = top.reduce((acc, l) => acc + Math.sqrt(l[2]), 0) || 1;
    top.forEach(([i, j, w]) => {
      const count = Math.max(1, Math.round((budget * 0.28 * Math.sqrt(w)) / lsum));
      for (let k = 0; k < count; k++) {
        const t = rand();
        const o = sphere(0.004 + 0.012 * Math.sin(Math.PI * t));
        push(i, j, t, o[0], o[1], o[2]);
      }
    });

    // Nebula haze around each cluster
    d.clusters.forEach((c) => {
      if (c.members.length < 3) return;
      const count = Math.round((budget * 0.12 * c.members.length) / d.n);
      for (let k = 0; k < count; k++) {
        const i = c.members[Math.floor(Math.pow(rand(), 1.6) * c.members.length)];
        const o = sphere(0.13);
        push(i, i, 0, o[0], o[1], o[2]);
      }
    });

    const buf = new Float32Array(parts);
    this.particleCount = buf.length / 7;
    this.particleVao = this.vao((gl) => {
      gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer());
      gl.bufferData(gl.ARRAY_BUFFER, buf, gl.STATIC_DRAW);
      gl.enableVertexAttribArray(0);
      gl.vertexAttribPointer(0, 4, gl.FLOAT, false, 28, 0);
      gl.enableVertexAttribArray(1);
      gl.vertexAttribPointer(1, 3, gl.FLOAT, false, 28, 16);
    });
  }

  resize(w, h) {
    if (this.canvas.width !== w || this.canvas.height !== h) {
      this.canvas.width = w;
      this.canvas.height = h;
    }
  }

  ensureFbo(w, h) {
    const gl = this.gl;
    if (this.fbo && this.fboW === w && this.fboH === h) return;
    if (this.fbo) { gl.deleteFramebuffer(this.fbo); gl.deleteTexture(this.fboTex); }
    this.fboTex = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, this.fboTex);
    if (this.floatFbo) gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA16F, w, h, 0, gl.RGBA, gl.HALF_FLOAT, null);
    else gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA8, w, h, 0, gl.RGBA, gl.UNSIGNED_BYTE, null);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    this.fbo = gl.createFramebuffer();
    gl.bindFramebuffer(gl.FRAMEBUFFER, this.fbo);
    gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, this.fboTex, 0);
    gl.bindFramebuffer(gl.FRAMEBUFFER, null);
    this.fboW = w; this.fboH = h;
  }

  common(prog, s) {
    const gl = this.gl, u = prog.u;
    gl.useProgram(prog.p);
    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D, this.nodeTex);
    gl.uniform1i(u.u_nodes, 0);
    gl.uniformMatrix4fv(u.u_vp, false, s.vp);
    gl.uniform1f(u.u_morph, s.morph);
    gl.uniform1f(u.u_time, s.time);
    gl.uniform1f(u.u_scale, WORLD_SCALE);
    gl.uniform1f(u.u_pr, s.pr);
    gl.uniform1f(u.u_intro, s.intro);
    gl.uniform1f(u.u_focal, s.focal);
  }

  render(s) {
    const gl = this.gl, W = this.canvas.width, H = this.canvas.height;
    gl.bindFramebuffer(gl.FRAMEBUFFER, null);
    gl.viewport(0, 0, W, H);
    gl.disable(gl.DEPTH_TEST);
    gl.clearColor(this.bg[0], this.bg[1], this.bg[2], 1);
    gl.clear(gl.COLOR_BUFFER_BIT);

    const density = s.view === "density";
    if (density && this.n) this.renderDensity(s, W, H);

    gl.enable(gl.BLEND);
    gl.blendFunc(gl.ONE, gl.ONE);

    if (s.dust > 0 && this.particleCount) {
      const p = this.progParticles;
      this.common(p, s);
      gl.uniform1f(p.u.u_size, 2.1);
      gl.uniform1f(p.u.u_alpha, 0.5 * s.dust * (density ? 0.3 : 1));
      gl.uniform1f(p.u.u_hlActive, s.hlActive ? 1 : 0);
      gl.bindVertexArray(this.particleVao);
      gl.drawArrays(gl.POINTS, 0, this.particleCount);
    }

    if (!density && this.edgeCount && s.maxRank > 0 || s.hlActive && this.edgeCount) {
      const p = this.progEdges;
      this.common(p, s);
      gl.uniform1f(p.u.u_maxRank, density ? 0 : s.maxRank);
      gl.uniform1f(p.u.u_edgeAlpha, s.edgeAlpha);
      gl.uniform1f(p.u.u_hlActive, s.hlActive ? 1 : 0);
      gl.bindVertexArray(this.edgeVao);
      gl.drawArrays(gl.LINES, 0, this.edgeCount);
    }

    if (this.n) {
      const p = this.progNodes;
      this.common(p, s);
      gl.uniform1f(p.u.u_nodeScale, density ? 0.45 : 1);
      gl.uniform1f(p.u.u_hlActive, s.hlActive ? 1 : 0);
      gl.bindVertexArray(this.nodeVao);
      gl.drawArrays(gl.POINTS, 0, this.n);
    }
    gl.bindVertexArray(null);
  }

  renderDensity(s, W, H) {
    const gl = this.gl;
    const fw = Math.max(1, Math.round(W / 2)), fh = Math.max(1, Math.round(H / 2));
    this.ensureFbo(fw, fh);
    gl.bindFramebuffer(gl.FRAMEBUFFER, this.fbo);
    gl.viewport(0, 0, fw, fh);
    gl.clearColor(0, 0, 0, 0);
    gl.clear(gl.COLOR_BUFFER_BIT);
    gl.enable(gl.BLEND);
    gl.blendFunc(gl.ONE, gl.ONE);
    const sp = this.progSplat;
    this.common(sp, s);
    gl.uniform1f(sp.u.u_kernel, 0.17);
    gl.uniform1f(sp.u.u_focalPx, fh / (2 * Math.tan(s.fov / 2)));
    gl.uniform1f(sp.u.u_splatScale, this.floatFbo ? 1 : 0.12);
    gl.bindVertexArray(this.nodeVao);
    gl.drawArrays(gl.POINTS, 0, this.n);

    gl.bindFramebuffer(gl.FRAMEBUFFER, null);
    gl.viewport(0, 0, W, H);
    gl.disable(gl.BLEND);
    const dp = this.progDensity;
    gl.useProgram(dp.p);
    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D, this.fboTex);
    gl.uniform1i(dp.u.u_dens, 0);
    gl.activeTexture(gl.TEXTURE1);
    gl.bindTexture(gl.TEXTURE_2D, this.lutTex);
    gl.uniform1i(dp.u.u_lut, 1);
    gl.uniform1f(dp.u.u_gain, this.floatFbo ? 0.55 : 4.5);
    gl.uniform3fv(dp.u.u_bg, this.bg);
    gl.bindVertexArray(this.emptyVao);
    gl.drawArrays(gl.TRIANGLES, 0, 3);
    gl.activeTexture(gl.TEXTURE0);
  }
}

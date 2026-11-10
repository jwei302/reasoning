// Chart builders shared by the project page and the poster. Every figure is drawn from window.DATA
// (written by scripts/build_data.py) in the style of the extrapolation page: boxed axes, a serif face,
// light grids and tab10-like colors. Each builder takes an <svg> and draws into it.
(function () {
  "use strict";
  const NS = "http://www.w3.org/2000/svg";
  const COL = {
    astra: "#8669af", opus: "#377f94", fable: "#489767",
    none: "#7f7f7f", see: "#1f77b4", touch: "#d62728",
    mae: "#ff7f0e", dino: "#2ca02c", dinov2: "#9467bd",
    ref: "#595959", published: "#d97a1e", linear: "#8c8c8c", mlp: "#b5b5b5",
    sizes: ["#9ecae1", "#6baed6", "#2f7fc1", "#0b3f80"],
    efforts: ["#d9cbe9", "#b9a0d8", "#9473c3", "#6c45a3", "#43226f"],
  };
  const EFF = ["low", "medium", "high", "xhigh", "max"];
  let uid = 0;

  function el(tag, attrs, parent) {
    const n = document.createElementNS(NS, tag);
    if (attrs) for (const k in attrs) if (attrs[k] != null) n.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(n);
    return n;
  }
  // SVG text with light markup: ~x~ italic, _x subscript, ^x superscript (braces for longer runs)
  function label(parent, x, y, spec, attrs) {
    const t = el("text", Object.assign({ x, y, "font-size": 13, fill: "#000" }, attrs || {}), parent);
    let shift = 0;
    for (const tok of String(spec).match(/~[^~]+~|[_^](?:\{[^}]*\}|[^\s~_^])|[^~_^]+/g) || []) {
      const s = el("tspan", {}, t);
      let text = tok, want = 0;
      if (tok[0] === "~") { text = tok.slice(1, -1); s.setAttribute("font-style", "italic"); }
      else if (tok[0] === "_" || tok[0] === "^") {
        text = tok.slice(1).replace(/^\{|\}$/g, ""); want = tok[0] === "_" ? 4 : -6;
        s.setAttribute("font-size", "72%");
      }
      if (want !== shift) { s.setAttribute("dy", want - shift); shift = want; }
      s.textContent = text;
    }
    return t;
  }
  function clip(svg, x, y, w, h) {
    const id = "clip" + (++uid), cp = el("clipPath", { id }, el("defs", {}, svg));
    el("rect", { x, y, width: w, height: h }, cp);
    return `url(#${id})`;
  }
  const pathOf = pts => pts.map((p, i) => (i ? "L" : "M") + p[0].toFixed(1) + " " + p[1].toFixed(1)).join(" ");
  function marker(kind, x, y, color, parent, s) {
    const k = s || 1, a = { fill: color, stroke: "#fff", "stroke-width": 0.8 };
    if (kind === "s") return el("rect", Object.assign({ x: x - 3.2 * k, y: y - 3.2 * k, width: 6.4 * k, height: 6.4 * k }, a), parent);
    if (kind === "^") return el("path", Object.assign({ d: `M${x} ${y - 4.3 * k}L${x + 4 * k} ${y + 3 * k}L${x - 4 * k} ${y + 3 * k}Z` }, a), parent);
    if (kind === "d") return el("path", Object.assign({ d: `M${x} ${y - 4.4 * k}L${x + 3.6 * k} ${y}L${x} ${y + 4.4 * k}L${x - 3.6 * k} ${y}Z` }, a), parent);
    if (kind === "v") return el("path", Object.assign({ d: `M${x} ${y + 4.3 * k}L${x + 4 * k} ${y - 3 * k}L${x - 4 * k} ${y - 3 * k}Z` }, a), parent);
    return el("circle", Object.assign({ cx: x, cy: y, r: 3.6 * k }, a), parent);
  }

  // Boxed axes. x and y are {lim, ticks, label, log, cats}. Categorical x uses cats and integer positions.
  function axes(svg, o) {
    const W = o.W || 400, H = o.H || 300, m = Object.assign({ l: 58, r: 14, t: 34, b: 50 }, o.m || {});
    const fs = o.fs || 1;
    svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
    svg.textContent = "";
    const x0 = m.l, x1 = W - m.r, y0 = m.t, y1 = H - m.b;
    const xs = o.x, ys = o.y;
    if (xs.cats) { xs.lim = xs.lim || [-0.45, xs.cats.length - 0.55]; xs.ticks = xs.cats.map((c, i) => ({ v: i, l: c })); }
    const fx = xs.log ? Math.log10 : v => v, fy = ys.log ? Math.log10 : v => v;
    const X = v => x0 + (fx(v) - fx(xs.lim[0])) / (fx(xs.lim[1]) - fx(xs.lim[0])) * (x1 - x0);
    const Y = v => y1 - (fy(v) - fy(ys.lim[0])) / (fy(ys.lim[1]) - fy(ys.lim[0])) * (y1 - y0);
    el("rect", { x: x0, y: y0, width: x1 - x0, height: y1 - y0, fill: "#fff" }, svg);
    const grid = el("g", {}, svg), refs = el("g", {}, svg);
    const data = el("g", { "clip-path": clip(svg, x0 - 6, y0 - 6, x1 - x0 + 12, y1 - y0 + 12) }, svg);
    const top = el("g", {}, svg);
    const tick = { stroke: "#000", "stroke-width": 0.9 };
    for (const t of xs.ticks || []) {
      const x = X(t.v);
      if (o.grid !== false && !xs.cats) el("line", { x1: x, x2: x, y1: y0, y2: y1, stroke: "#000", "stroke-opacity": 0.07 }, grid);
      el("line", Object.assign({ x1: x, x2: x, y1: y1, y2: y1 + 5 }, tick), top);
      label(top, x, y1 + 6 + 13 * fs, t.l, { "text-anchor": "middle", "font-size": 13 * fs });
    }
    for (const t of ys.ticks || []) {
      const y = Y(t.v);
      if (o.grid !== false) el("line", { x1: x0, x2: x1, y1: y, y2: y, stroke: "#000", "stroke-opacity": 0.07 }, grid);
      el("line", Object.assign({ x1: x0 - 5, x2: x0, y1: y, y2: y }, tick), top);
      label(top, x0 - 8, y + 4.5 * fs, t.l, { "text-anchor": "end", "font-size": 13 * fs });
    }
    if (xs.label) label(top, (x0 + x1) / 2, y1 + 12 + 30 * fs, xs.label, { "text-anchor": "middle", "font-size": 14 * fs });
    if (ys.label) {
      const lx = x0 - (o.ylabelGap || 46) * fs;
      label(top, lx, (y0 + y1) / 2, ys.label, { "text-anchor": "middle", "font-size": 14 * fs, transform: `rotate(-90 ${lx} ${(y0 + y1) / 2})` });
    }
    if (o.title) label(top, (x0 + x1) / 2, y0 - 11, o.title, { "text-anchor": "middle", "font-size": 15 * fs, "font-weight": 600 });
    el("rect", { x: x0, y: y0, width: x1 - x0, height: y1 - y0, fill: "none", stroke: "#000", "stroke-width": 1 }, top);
    return { X, Y, grid, refs, data, top, x0, x1, y0, y1, fs, svg };
  }

  // A horizontal reference line with its label at the right end, above the line unless told otherwise.
  function ref(A, y, text, o) {
    const p = o || {}, yy = A.Y(y), color = p.color || COL.ref;
    el("line", { x1: A.x0, x2: A.x1, y1: yy, y2: yy, stroke: color, "stroke-width": 1.1, "stroke-dasharray": p.dash || "2 3" }, A.refs);
    // Sit the label under its line when the line is close to the top of the frame, so it stays inside.
    const below = p.below || yy - A.y0 < 14 * A.fs;
    if (text) label(A.top, p.left ? A.x0 + 6 : A.x1 - 5, yy + (below ? 12 : -4) * A.fs, text, { "text-anchor": p.left ? "start" : "end", "font-size": 11.5 * A.fs, fill: color });
  }

  // Lines with markers, optional error bars (lo, hi) and an optional shaded band.
  function series(A, s) {
    const pts = s.pts.filter(p => p.y != null);
    const g = el("g", { opacity: s.opacity }, A.data);
    if (s.band) {
      const up = pts.map(p => [A.X(p.x), A.Y(p.hi)]), dn = pts.map(p => [A.X(p.x), A.Y(p.lo)]).reverse();
      el("path", { d: pathOf(up.concat(dn)) + "Z", fill: s.color, "fill-opacity": 0.12, stroke: "none" }, g);
    }
    if (s.err) for (const p of pts) if (p.lo != null) el("line", { x1: A.X(p.x), x2: A.X(p.x), y1: A.Y(p.lo), y2: A.Y(p.hi), stroke: s.color, "stroke-width": 1.2 }, g);
    if (s.dots) for (const p of pts) for (const v of p.vals || []) el("circle", { cx: A.X(p.x) + (s.dotShift || 0), cy: A.Y(v), r: 2.3, fill: s.color, "fill-opacity": 0.35 }, g);
    if (s.line !== false) el("path", { d: pathOf(pts.map(p => [A.X(p.x), A.Y(p.y)])), fill: "none", stroke: s.color, "stroke-width": s.width || 2, "stroke-dasharray": s.dash, "stroke-linejoin": "round" }, g);
    if (s.marker !== null) for (const p of pts) marker(s.marker || "o", A.X(p.x), A.Y(p.y), s.color, g, s.ms);
    return g;
  }

  // Legend box. items: {text, color, marker, dash, area}
  function legend(A, x, y, items, o) {
    const p = o || {}, fs = (p.fs || 1) * A.fs, rowH = 18 * fs, pad = 6 * fs, sample = 22 * fs;
    const g = el("g", {}, A.top);
    const box = el("rect", { x, y, rx: 3, fill: "#fff", "fill-opacity": 0.93, stroke: "#c8c8c8" }, g);
    const cols = p.cols || 1, per = Math.ceil(items.length / cols);
    const texts = [];
    items.forEach((it, i) => {
      const c = Math.floor(i / per), r = i % per;
      const gx = el("g", {}, g), cy = y + pad + rowH * r + rowH / 2;
      gx.dataset.col = c;
      if (it.area) el("rect", { x: x + pad, y: cy - 5 * fs, width: sample, height: 10 * fs, fill: it.color, "fill-opacity": it.opacity || 1 }, gx);
      else if (it.line !== false) el("line", { x1: x + pad, x2: x + pad + sample, y1: cy, y2: cy, stroke: it.color, "stroke-width": 2, "stroke-dasharray": it.dash }, gx);
      if (it.marker) marker(it.marker, x + pad + sample / 2, cy, it.color, gx, 0.9);
      texts.push({ g: gx, c, t: label(gx, x + pad + sample + 6 * fs, cy + 4.3 * fs, it.text, { "font-size": 12 * fs }) });
    });
    const layout = () => {
      const widths = [];
      texts.forEach(t => { widths[t.c] = Math.max(widths[t.c] || 0, t.t.getComputedTextLength()); });
      const colW = widths.map(w => pad + sample + 6 * fs + w + pad);
      let off = 0;
      colW.forEach((w, c) => { texts.filter(t => t.c === c).forEach(t => t.g.setAttribute("transform", `translate(${off} 0)`)); off += w; });
      box.setAttribute("width", off + pad * 0.5); box.setAttribute("height", pad * 2 + rowH * per);
      if (p.anchor === "right") g.setAttribute("transform", `translate(${-(off + pad * 0.5)} 0)`);
      if (p.valign === "bottom") g.setAttribute("transform", (p.anchor === "right" ? `translate(${-(off + pad * 0.5)} ` : "translate(0 ") + `${-(pad * 2 + rowH * per)})`);
    };
    layout();
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(layout);
    return g;
  }

  const fmt = (v, d) => (v < 0 ? "−" : "") + Math.abs(v).toFixed(d);
  const range = (a, b, step) => { const out = []; for (let v = a; v <= b + 1e-9; v += step) out.push(+v.toFixed(6)); return out; };
  const tks = (vs, d) => vs.map(v => ({ v, l: fmt(v, d) }));
  const effortAxis = (label) => ({ cats: EFF, label: label || "Reasoning effort" });
  const effortPts = (obj, f) => EFF.map((e, i) => (obj[e] == null ? null : Object.assign({ x: i }, f(obj[e])))).filter(Boolean);
  const D = () => window.DATA;

  /* ============================================================ mathematics */

  const QWEN = ["qwen3-0.6b", "qwen3-1.7b", "qwen3-4b", "qwen3-8b"];
  const QWEN_LABEL = { "qwen3-0.6b": "Qwen3-0.6B", "qwen3-1.7b": "Qwen3-1.7B", "qwen3-4b": "Qwen3-4B", "qwen3-8b": "Qwen3-8B" };
  const sizeTicks = vs => vs.map(v => ({ v, l: v + "B" }));

  function statement(svg, fam, o) {
    const p = o || {}, rows = D().mathematics.statement.families[fam || "Qwen3"];
    const emb = fam === "Qwen3-Embedding";
    const A = axes(svg, {
      W: p.W || 400, H: p.H || 310, fs: p.fs, title: p.title === undefined ? `${fam || "Qwen3"}: statement and proof` : p.title,
      x: { log: true, lim: [0.48, 10], ticks: sizeTicks(rows.map(r => r.params)), label: "Parameters" },
      y: { lim: emb ? [0.05, 0.4] : [0, 0.3], ticks: tks(emb ? range(0.1, 0.4, 0.1) : range(0, 0.3, 0.05), 2), label: "Mutual ~k~-NN alignment" },
    });
    ref(A, D().mathematics.statement.tfidf, "Word overlap floor", { below: true });
    const pts = (k) => rows.map(r => ({ x: r.params, y: r[k], lo: r[k + "_ci"][0], hi: r[k + "_ci"][1] }));
    series(A, { pts: pts("matched"), color: COL.see, band: true });
    if (!p.simple) series(A, { pts: pts("cross"), color: COL.see, band: true, dash: "5 3", marker: "^" });
    series(A, { pts: pts("mismatched"), color: COL.touch, band: true, marker: "s" });
    const items = [{ text: "Statement with its own proof", color: COL.see, marker: "o" }];
    if (!p.simple) items.push({ text: "Same, neighbours from other papers", color: COL.see, marker: "^", dash: "5 3" });
    items.push({ text: "Statement with another proof", color: COL.touch, marker: "s" });
    legend(A, A.x0 + 8, A.y0 + 8, items, { fs: 0.92 });
    return A;
  }

  function edits(svg, fam, o) {
    const p = o || {}, rows = D().mathematics.statement.families[fam || "Qwen3"];
    const emb = fam === "Qwen3-Embedding";
    const A = axes(svg, {
      W: p.W || 400, H: p.H || 310, fs: p.fs, title: `${fam}: edited proofs`,
      x: { log: true, lim: [0.48, 10], ticks: sizeTicks(rows.map(r => r.params)), label: "Parameters" },
      y: { lim: emb ? [0.24, 0.4] : [0.14, 0.36], ticks: tks(emb ? range(0.25, 0.4, 0.05) : range(0.15, 0.35, 0.05), 2), label: "Mutual ~k~-NN alignment" },
    });
    const kinds = [["original", "Original proof", COL.see, "o"], ["rewrite", "True rewrite", "#ff7f0e", "s"], ["flip", "One inequality flipped", "#2ca02c", "^"], ["flip_all", "Every inequality flipped", "#bcbd22", "d"], ["shuffle", "Sentences shuffled", "#e377c2", "v"]];
    series(A, { pts: rows.map(r => ({ x: r.params, y: r.edits.original, lo: r.edits.original_ci[0], hi: r.edits.original_ci[1] })), color: COL.see, band: true, line: false, marker: null });
    for (const [k, , c, m] of kinds) series(A, { pts: rows.map(r => ({ x: r.params, y: r.edits[k] })), color: c, marker: m, width: 1.6 });
    legend(A, A.x0 + 8, A.y0 + 8, kinds.map(([, t, c, m]) => ({ text: t, color: c, marker: m })), { fs: 0.9 });
    return A;
  }

  function ladderCaps(svg, o) {
    const p = o || {}, L = D().mathematics.ladder;
    const caps = [1024, 2048, 4096, 8192, 16384, 32768];
    const A = axes(svg, {
      W: p.W || 400, H: p.H || 310, fs: p.fs, title: "Qwen3 size ladder",
      x: { log: true, lim: [800, 42000], ticks: caps.map(c => ({ v: c, l: c / 1024 + "K" })), label: "Reasoning token cap" },
      y: { lim: [0, 100], ticks: tks(range(0, 100, 20), 0), label: "Verification macro F1 (%)" },
    });
    const names = ["Qwen/Qwen3-0.6B", "Qwen/Qwen3-1.7B", "Qwen/Qwen3-4B", "Qwen/Qwen3-8B"];
    names.forEach((n, i) => series(A, { pts: L[n].points.map(q => ({ x: q.cap, y: q.f1 })), color: COL.sizes[i], marker: ["o", "s", "^", "d"][i] }));
    legend(A, A.x1 - 8, A.y1 - 8, names.map((n, i) => ({ text: n.split("/")[1], color: COL.sizes[i], marker: ["o", "s", "^", "d"][i] })), { anchor: "right", valign: "bottom", fs: 0.9, cols: 2 });
    return A;
  }

  function ladderParams(svg, o) {
    const p = o || {}, L = D().mathematics.ladder;
    const A = axes(svg, {
      W: p.W || 400, H: p.H || 310, fs: p.fs, title: "At the largest cap",
      x: { log: true, lim: [0.48, 10], ticks: [{ v: 0.6, l: "0.6B" }, { v: 1.6, l: "1.5–1.7B" }, { v: 4, l: "4B" }, { v: 7.5, l: "7–8B" }], label: "Parameters" },
      y: { lim: [0, 100], ticks: tks(range(0, 100, 20), 0), label: "Verification macro F1 (%)" },
    });
    const last = n => L[n].points[L[n].points.length - 1];
    const fam = [
      ["Qwen3", COL.see, "o", [["Qwen/Qwen3-0.6B", 0.6], ["Qwen/Qwen3-1.7B", 1.7], ["Qwen/Qwen3-4B", 4], ["Qwen/Qwen3-8B", 8]], undefined],
      ["Math RL (RLinf)", COL.dinov2, "s", [["RLinf/RLinf-math-1.5B", 1.5], ["RLinf/RLinf-math-7B", 7]], "5 3"],
      ["Distilled parent (DeepSeek)", "#444", "^", [["deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B", 1.5], ["deepseek-ai/DeepSeek-R1-Distill-Qwen-7B", 7]], "2 3"],
    ];
    for (const [, c, m, ms, dash] of fam) series(A, { pts: ms.map(([n, x]) => { const q = last(n); return { x, y: q.f1, lo: q.ci[0], hi: q.ci[1] }; }), color: c, marker: m, err: true, dash });
    legend(A, A.x1 - 8, A.y1 - 8, fam.map(([t, c, m, , dash]) => ({ text: t, color: c, marker: m, dash })), { anchor: "right", valign: "bottom", fs: 0.9 });
    return A;
  }

  function gaps(svg, o) {
    const p = o || {}, G = D().mathematics.gaps;
    const caps = [0, 1024, 2048, 4096, 8192, 16384];
    const A = axes(svg, {
      W: p.W || 640, H: p.H || 300, fs: p.fs, title: p.title === undefined ? "Filling a hidden proof step" : p.title,
      x: { cats: caps.map(c => (c ? c / 1024 + "K" : "none")), label: "Reasoning token cap" },
      y: { lim: [0, 16], ticks: tks(range(0, 16, 4), 0), label: "Fills stating the hidden step (%)" },
    });
    QWEN.forEach((k, i) => series(A, { pts: G[k].map(q => ({ x: caps.indexOf(q.cap), y: q.rate, lo: q.ci[0], hi: q.ci[1] })), color: COL.sizes[i], marker: ["o", "s", "^", "d"][i], err: i >= 2 }));
    legend(A, A.x1 - 8, A.y0 + 8, QWEN.map((k, i) => ({ text: QWEN_LABEL[k], color: COL.sizes[i], marker: ["o", "s", "^", "d"][i] })), { anchor: "right", fs: 0.92, cols: 2 });
    return A;
  }

  /* ================================================================== touch */

  const ENC = [["vision", "Vision", "DINOv2"], ["touch:mae-base", "Touch", "MAE"], ["touch:dino-base", "Touch", "DINO"], ["touch:dinov2-base", "Touch", "DINOv2"]];
  const CUES = [["none", "No cue", COL.none], ["see", "See cue", COL.see], ["touch", "Touch cue", COL.touch]];

  function cueBars(svg, mode, o) {
    const p = o || {}, M = D().touch.modes[mode];
    const A = axes(svg, {
      W: p.W || 400, H: p.H || 300, fs: p.fs, title: mode === "z_e" ? "Reading the prompt" : "After generating text",
      x: { cats: ENC.map(e => e[2]), label: "Encoder" },
      y: { lim: [0, 0.065], ticks: tks(range(0, 0.06, 0.02), 2), label: "Mutual ~k~-NN alignment" },
      m: { l: 60, b: 50 },
    });
    const bw = 0.24;
    ENC.forEach(([k], i) => CUES.forEach(([c, , col], j) => {
      const x = A.X(i + (j - 1) * bw), v = M[k][c];
      el("rect", { x: x - (A.X(bw) - A.X(0)) / 2, y: A.Y(v), width: A.X(bw) - A.X(0) - 1, height: A.Y(0) - A.Y(v), fill: col, stroke: "#222", "stroke-width": 0.5 }, A.data);
    }));
    el("line", { x1: A.X(0.5), x2: A.X(0.5), y1: A.y0, y2: A.y1, stroke: "#000", "stroke-opacity": 0.25, "stroke-dasharray": "3 3" }, A.refs);
    label(A.top, A.X(2), A.y0 + 16, "Tactile encoders", { "text-anchor": "middle", "font-size": 12 * A.fs, fill: "#555" });
    if (p.legend !== false) legend(A, A.x1 - 8, A.y0 + 24, CUES.map(([, t, c]) => ({ text: t, color: c, area: true })), { anchor: "right", fs: 0.9 });
    return A;
  }

  const LENGTHS = [["z_e", "read"], ["z_g128", "128"], ["z_g256", "256"], ["z_g512", "512"]];
  const meanTouch = (m, c) => (m["touch:mae-base"][c] + m["touch:dino-base"][c] + m["touch:dinov2-base"][c]) / 3;

  function lengthPlot(svg, which, o) {
    const p = o || {}, T = D().touch.modes;
    const vision = which === "vision";
    const A = axes(svg, {
      W: p.W || 400, H: p.H || 300, fs: p.fs, title: p.title === undefined ? (vision ? "Alignment with vision" : "Alignment with touch") : p.title,
      x: { cats: LENGTHS.map(l => l[1]), label: "Tokens generated" },
      y: vision ? { lim: [0.042, 0.062], ticks: tks(range(0.045, 0.06, 0.005), 3), label: "Mutual ~k~-NN alignment" }
        : { lim: [0.0165, 0.0215], ticks: tks(range(0.017, 0.021, 0.001), 3), label: "Mean tactile alignment" },
      m: { l: 64 }, ylabelGap: 52,
    });
    for (const [c, , col] of CUES) series(A, { pts: LENGTHS.map(([k], i) => ({ x: i, y: vision ? T[k].vision[c] : meanTouch(T[k], c) })), color: col, marker: "o" });
    if (p.legend !== false) legend(A, A.x1 - 8, vision ? A.y0 + 8 : A.y1 - 8, CUES.map(([, t, c]) => ({ text: t, color: c, marker: "o" })), { anchor: "right", valign: vision ? null : "bottom", fs: 0.9 });
    return A;
  }

  const TACT = [["sparsh-mae-base", "MAE", COL.mae, "o"], ["sparsh-dino-base", "DINO", COL.dino, "s"], ["sparsh-dinov2-base", "DINOv2", COL.dinov2, "^"]];
  function scalePlot(svg, which, o) {
    const p = o || {}, S = D().touch.scale[which];
    const vision = which === "vision";
    const cats = vision ? ["S", "B", "L", "G"] : ["0.6B", "1.7B", "8B"];
    const A = axes(svg, {
      W: p.W || 400, H: p.H || 300, fs: p.fs, title: vision ? "Touch against vision size" : "Touch against language size",
      x: { cats, label: vision ? "DINOv2 size" : "Qwen3 size" },
      y: vision ? { lim: [0.054, 0.064], ticks: tks(range(0.055, 0.064, 0.003), 3), label: "Mutual ~k~-NN alignment" }
        : { lim: [0.018, 0.023], ticks: tks(range(0.018, 0.023, 0.001), 3), label: "Mutual ~k~-NN alignment" },
      m: { l: 64 }, ylabelGap: 52,
    });
    for (const [k, , c, m] of TACT) series(A, { pts: S[k].map((v, i) => ({ x: i, y: v })), color: c, marker: m });
    legend(A, A.x0 + 8, A.y0 + 8, TACT.map(([, t, c, m]) => ({ text: "Touch " + t, color: c, marker: m })), { fs: 0.9 });
    return A;
  }

  function imagine(svg, o) {
    const p = o || {}, I = D().touch.imagine, B = D().touch.imagine_baselines;
    const A = axes(svg, {
      W: p.W || 640, H: p.H || 300, fs: p.fs, title: p.title === undefined ? "Predicting tactile maps from an image" : p.title,
      x: effortAxis(),
      y: { lim: [0.009, 0.016], ticks: tks(range(0.009, 0.016, 0.001), 3), label: "Tactile map MSE (lower is better)" },
      m: { l: 66 }, ylabelGap: 54,
    });
    ref(A, B["Zero signal"], "Predict no contact", { left: true });
    ref(A, B["Training mean (fixed sample)"], "Predict the training mean", { left: true, below: true });
    const fams = [["gpt-6-astra", "GPT-6 Astra", COL.astra, -0.08], ["claude-opus-5-5", "Claude Opus 5.5", COL.opus, 0.08], ["claude-fable-5-1", "Claude Fable 5.1", COL.fable, 0]];
    for (const [k, , c, dx] of fams) if (I[k]) series(A, { pts: effortPts(I[k], v => ({ y: v.mse, lo: v.ci[0], hi: v.ci[1] })).map(q => Object.assign(q, { x: q.x + dx })), color: c, err: true });
    legend(A, A.x1 - 8, A.y0 + 8, fams.map(([, t, c]) => ({ text: t, color: c, marker: "o" })), { anchor: "right", fs: 0.9, cols: 3 });
    return A;
  }

  /* ================================================================= digits */

  const REGIMES = [["full", "Fifty thousand labelled images", "o", undefined], ["ten", "Ten labelled images", "s", "6 3"], ["none", "No images", "^", "2 3"]];
  function digitRefs(A, which) {
    const R = D().digits.references;
    for (const r of R) if (which.some(w => r.label.startsWith(w))) {
      const name = r.label.startsWith("linear") ? "Linear classifier" : r.label.startsWith("multilayer") ? "MLP, one hidden layer" : r.label.startsWith("convolutional network") ? "Convolutional network" : "Convolutional ensemble";
      ref(A, r.accuracy, name + " (trained)", { below: r.label.startsWith("multilayer") && which.length > 2 });
    }
  }

  function digitRegimes(svg, fam, o) {
    const p = o || {}, R = D().digits.regimes, col = fam === "Astra" ? COL.astra : COL.opus;
    const A = axes(svg, {
      W: p.W || 400, H: p.H || 320, fs: p.fs, title: fam === "Astra" ? "GPT-6 Astra" : "Claude Opus 5.5",
      x: effortAxis(), y: { lim: [70, 100], ticks: tks(range(70, 100, 5), 0), label: "Held-out accuracy (%)" },
    });
    digitRefs(A, ["linear", "multilayer", "convolutional network"]);
    for (const [k, , m, dash] of REGIMES) series(A, { pts: effortPts(R[k][fam], v => ({ y: v })), color: col, marker: m, dash, opacity: k === "full" ? 1 : 0.85 });
    if (p.legend !== false) legend(A, A.x1 - 8, A.y1 - 8, REGIMES.map(([, t, m, dash]) => ({ text: t, color: col, marker: m, dash })), { anchor: "right", valign: "bottom", fs: 0.88 });
    return A;
  }

  function weights(svg, o) {
    const p = o || {}, R = D().digits.regimes;
    const A = axes(svg, {
      W: p.W || 640, H: p.H || 320, fs: p.fs, title: p.title === undefined ? "Networks whose every weight was written by reasoning" : p.title,
      x: effortAxis(), y: { lim: [76, 100], ticks: tks(range(76, 100, 4), 0), label: "Held-out accuracy (%)" },
    });
    digitRefs(A, ["linear", "multilayer", "convolutional network"]);
    if (!p.simple) {
      series(A, { pts: effortPts(R.full.Astra, v => ({ y: v })), color: COL.astra, dash: "4 3", width: 1.3, opacity: 0.45, ms: 0.75 });
      series(A, { pts: effortPts(R.full.Opus, v => ({ y: v })), color: COL.opus, dash: "4 3", width: 1.3, opacity: 0.45, ms: 0.75 });
    }
    series(A, { pts: effortPts(R.weights.Astra, v => ({ y: v })), color: COL.astra, width: 2.6, ms: 1.2 });
    series(A, { pts: effortPts(R.weights.Opus, v => ({ y: v })), color: COL.opus, width: 2.6, ms: 1.2 });
    const items = [{ text: "GPT-6 Astra, written weights", color: COL.astra, marker: "o" }, { text: "Claude Opus 5.5, written weights", color: COL.opus, marker: "o" }];
    if (!p.simple) items.push({ text: "Same models, free-form programs", color: "#999", dash: "4 3" });
    legend(A, A.x1 - 8, A.y1 - 8, items, { anchor: "right", valign: "bottom", fs: 0.9 });
    return A;
  }

  // Validation error during gradient training, starting from the written weights, one line per effort.
  function initCurves(svg, o) {
    const p = o || {}, C = D().digits.curves.Astra;
    const A = axes(svg, {
      W: p.W || 400, H: p.H || 310, fs: p.fs, title: p.title === undefined ? "Training from written weights" : p.title,
      x: { lim: [0, 7820], ticks: [0, 2000, 4000, 6000].map(v => ({ v, l: String(v) })), label: "Gradient updates" },
      y: { log: true, lim: [0.6, 30], ticks: [1, 3, 10, 30].map(v => ({ v, l: String(v) })), label: "Validation error (%)" },
    });
    EFF.forEach((e, i) => series(A, { pts: C.authored[e].map(([x, y]) => ({ x, y })), color: COL.efforts[i], marker: null, width: 2 }));
    if (p.random) series(A, { pts: C.random.high.map(([x, y]) => ({ x, y })), color: "#999", marker: null, dash: "4 3", width: 1.4 });
    legend(A, A.x1 - 8, A.y0 + 8, EFF.map((e, i) => ({ text: "Astra " + e, color: COL.efforts[i] })), { anchor: "right", fs: 0.88 });
    return A;
  }

  function crossings(svg, o) {
    const p = o || {}, X = D().digits.crossings.Astra;
    const A = axes(svg, {
      W: p.W || 400, H: p.H || 310, fs: p.fs, title: p.title === undefined ? "Updates to reach 98% accuracy" : p.title,
      x: effortAxis("Effort that wrote the weights"),
      y: { log: true, lim: [250, 8000], ticks: [300, 1000, 3000].map(v => ({ v, l: String(v) })), label: "Gradient updates" },
    });
    series(A, { pts: effortPts(X, v => ({ y: v.random })), color: "#999", marker: "s", dash: "4 3" });
    series(A, { pts: effortPts(X, v => ({ y: v.authored })), color: COL.astra, width: 2.4, ms: 1.15 });
    legend(A, A.x0 + 8, A.y1 - 8, [{ text: "From written weights", color: COL.astra, marker: "o" }, { text: "From random weights", color: "#999", marker: "s", dash: "4 3" }], { valign: "bottom", fs: 0.9 });
    return A;
  }

  // Held-out error after the fixed training budget against effort rank, with the fitted power law e = A r^-alpha.
  function powerlaw(svg, o) {
    const p = o || {}, S = D().digits.scaling.filter(s => s.family === (p.family || "Astra"));
    const A = axes(svg, {
      W: p.W || 640, H: p.H || 300, fs: p.fs, title: p.title === undefined ? "Trained accuracy against reasoning effort" : p.title,
      x: { log: true, lim: [0.85, 5.8], ticks: EFF.map((e, i) => ({ v: i + 1, l: e })), label: "Effort that wrote the weights (log rank)" },
      y: { log: true, lim: [0.7, 2.2], ticks: [0.8, 1, 1.5, 2].map(v => ({ v, l: v.toFixed(1) })), label: "Held-out error after training (%)" },
    });
    const look = { authored: [COL.astra, "o", undefined, "From written weights"], random: ["#999", "s", "4 3", "From random weights"] };
    const items = [];
    for (const s of S) {
      const [c, m, dash, t] = look[s.condition];
      const fit = [];
      for (let r = 1; r <= 5.0001; r += 0.05) fit.push({ x: r, y: 100 * s.A * Math.pow(r, -s.alpha) });
      series(A, { pts: fit, color: c, marker: null, dash, width: 1.6, opacity: 0.9 });
      series(A, { pts: s.points.map(q => ({ x: q.rank, y: 100 - q.accuracy })), color: c, marker: m, line: false, ms: 1.15 });
      items.push({ text: `${t}: ~e~ ∝ ~r~^{−${s.alpha.toFixed(2)}}`, color: c, marker: m, dash });
    }
    legend(A, A.x0 + 8, A.y1 - 8, items, { valign: "bottom", fs: 0.9 });
    return A;
  }

  /* ================================================================ tabular */

  const LEARNED = [["Linear", "Linear", "|"], ["RandomForest", "Random forest", "s"], ["XGBoost", "XGBoost", "^"], ["CatBoost", "CatBoost", "d"], ["MLP", "MLP", "v"]];

  // One row per task. Each row has its own scale, oriented so that right is better.
  function tabLadder(svg, o) {
    const p = o || {}, T = D().tabular;
    const W = p.W || 760, rowH = 30 * (p.fs || 1), top = 34, H = top + rowH * T.length + 54;
    svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
    svg.textContent = "";
    const fs = p.fs || 1, lx = 210 * fs, x0 = lx + 14, x1 = W - 70 * fs;
    const g = el("g", {}, svg);
    label(g, x0, top - 16, "Worse", { "font-size": 12 * fs, fill: "#666" });
    label(g, x1, top - 16, "Better →", { "font-size": 12 * fs, fill: "#666", "text-anchor": "end" });
    let domain = null;
    T.forEach((t, i) => {
      const y = top + rowH * i + rowH / 2;
      if (i % 2 === 0) el("rect", { x: 0, y: y - rowH / 2, width: W, height: rowH, fill: "#f6f6f3" }, g);
      const vals = Object.values(t.learned);
      const best = { Astra: null, Opus: null };
      const effMeans = {};
      for (const f of ["Astra", "Opus"]) { effMeans[f] = (t.models[f] || []).map(q => q.mean); vals.push(...effMeans[f]); }
      let lo = Math.min(...vals), hi = Math.max(...vals);
      const pad = (hi - lo) * 0.06; lo -= pad; hi += pad;
      const S = v => (t.higher ? x0 + (v - lo) / (hi - lo) * (x1 - x0) : x1 - (v - lo) / (hi - lo) * (x1 - x0));
      el("line", { x1: x0, x2: x1, y1: y, y2: y, stroke: "#000", "stroke-opacity": 0.18 }, g);
      label(g, 8 * fs, y + 4.5 * fs, t.label, { "font-size": 13 * fs, "font-weight": 600 });
      label(g, lx, y + 4.5 * fs, t.domain, { "font-size": 11.5 * fs, fill: "#666", "text-anchor": "end" });
      for (const [k, , m] of LEARNED) {
        const v = t.learned[k]; if (v == null) continue;
        if (m === "|") el("line", { x1: S(v), x2: S(v), y1: y - 7, y2: y + 7, stroke: "#555", "stroke-width": 2 }, g);
        else marker(m, S(v), y, "#8c8c8c", g, 1.05);
      }
      [["Astra", COL.astra, -4], ["Opus", COL.opus, 4]].forEach(([f, c, dy]) => {
        const ms = effMeans[f]; if (!ms.length) return;
        const xs = ms.map(S);
        el("line", { x1: Math.min(...xs), x2: Math.max(...xs), y1: y + dy, y2: y + dy, stroke: c, "stroke-width": 3, "stroke-opacity": 0.45, "stroke-linecap": "round" }, g);
        const bi = t.higher ? ms.indexOf(Math.max(...ms)) : ms.indexOf(Math.min(...ms));
        marker("o", xs[bi], y + dy, c, g, 1.15);
      });
      label(g, x1 + 10 * fs, y + 4.5 * fs, t.metric === "rmse" ? "RMSE" : "AUROC", { "font-size": 11 * fs, fill: "#666" });
    });
    // Legend on two rows: the tuned learned models, then the two reasoning models.
    const ly = top + rowH * T.length + 20, rows = [[], []];
    const legendG = el("g", {}, svg);
    [["Linear", "|"], ["Random forest", "s"], ["XGBoost", "^"], ["CatBoost", "d"], ["MLP", "v"]].forEach(([t, m]) => {
      const gi = el("g", {}, legendG);
      if (m === "|") el("line", { x1: 6, x2: 6, y1: ly - 6, y2: ly + 6, stroke: "#555", "stroke-width": 2 }, gi);
      else marker(m, 6, ly, "#8c8c8c", gi, 1.05);
      rows[0].push({ gi, t: label(gi, 15, ly + 4.5 * fs, t, { "font-size": 12 * fs }), w: 15 });
    });
    [["GPT-6 Astra", COL.astra], ["Claude Opus 5.5", COL.opus]].forEach(([t, c]) => {
      const gi = el("g", {}, legendG);
      const y2 = ly + 20 * fs;
      el("line", { x1: 0, x2: 22, y1: y2, y2: y2, stroke: c, "stroke-width": 3, "stroke-opacity": 0.45, "stroke-linecap": "round" }, gi);
      marker("o", 22, y2, c, gi, 1.1);
      rows[1].push({ gi, t: label(gi, 31, y2 + 4.5 * fs, t + ", five effort settings", { "font-size": 12 * fs }), w: 31 });
    });
    const layout = () => {
      rows.forEach(parts => { let off = 8; parts.forEach(q => { q.gi.setAttribute("transform", `translate(${off} 0)`); off += q.w + q.t.getComputedTextLength() + 16; }); });
    };
    layout();
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(layout);
    svg.setAttribute("viewBox", `0 0 ${W} ${H + 20 * fs}`);
  }

  function tabTask(svg, idx, o) {
    const p = o || {}, t = D().tabular[idx];
    const vals = Object.values(t.learned).slice();
    for (const f of ["Astra", "Opus"]) for (const q of t.models[f] || []) vals.push(...q.values);
    let lo = Math.min(...vals), hi = Math.max(...vals);
    const span = hi - lo; lo -= span * 0.08; hi += span * 0.08;
    const step = niceStep((hi - lo) / 5), d = Math.max(0, -Math.floor(Math.log10(step) + 1e-9));
    const A = axes(svg, {
      W: p.W || 640, H: p.H || 310, fs: p.fs, title: p.title === undefined ? t.label : p.title, m: { l: 66, r: 128 }, ylabelGap: 54,
      x: effortAxis(),
      y: { lim: [lo, hi], ticks: tks(range(Math.ceil(lo / step) * step, hi, step), d), label: t.metric === "rmse" ? "Test RMSE (lower is better)" : "Test AUROC (higher is better)" },
    });
    // learned references, labelled in the right margin with collision avoidance
    const refsSorted = LEARNED.filter(([k]) => t.learned[k] != null).map(([k, n]) => ({ v: t.learned[k], n })).sort((a, b) => A.Y(a.v) - A.Y(b.v));
    let last = -1e9;
    for (const r of refsSorted) {
      const yy = A.Y(r.v);
      el("line", { x1: A.x0, x2: A.x1, y1: yy, y2: yy, stroke: COL.ref, "stroke-width": 1, "stroke-dasharray": "2 3" }, A.refs);
      const ty = Math.max(yy + 4, last + 13 * A.fs); last = ty;
      el("line", { x1: A.x1, x2: A.x1 + 6, y1: yy, y2: ty - 4, stroke: COL.ref, "stroke-width": 0.7 }, A.top);
      label(A.top, A.x1 + 8, ty, `${r.n} ${fmt(r.v, t.metric === "rmse" && r.v > 100 ? 0 : d + 1)}`, { "font-size": 11 * A.fs, fill: COL.ref });
    }
    [["Astra", COL.astra, -0.07], ["Opus", COL.opus, 0.07]].forEach(([f, c, dx]) => {
      const pts = (t.models[f] || []).map(q => ({ x: EFF.indexOf(q.effort) + dx, y: q.mean, lo: q.mean - q.sd, hi: q.mean + q.sd, vals: q.values }));
      series(A, { pts, color: c, err: true, dots: !p.simple });
    });
    if (p.legend !== false) legend(A, A.x0 + 8, A.y0 + 8, [{ text: "GPT-6 Astra", color: COL.astra, marker: "o" }, { text: "Claude Opus 5.5", color: COL.opus, marker: "o" }], { fs: 0.9, cols: 2 });
    return A;
  }
  function niceStep(raw) {
    const e = Math.pow(10, Math.floor(Math.log10(raw))), f = raw / e;
    return (f < 1.5 ? 1 : f < 3 ? 2 : f < 7 ? 5 : 10) * e;
  }

  /* ================================================================== ipSAE */

  function ipsaeTest(svg, idx, o) {
    const p = o || {}, t = D().ipsae.tests[idx];
    const cats = ["ipSAE", "Linear", "MLP", "Reasoned"];
    const auc = t.metric === "AUC";
    const A = axes(svg, {
      W: p.W || 260, H: p.H || 320, fs: p.fs, title: p.title === undefined ? t.label : p.title, m: { l: 52, r: 10, t: 46, b: 44 }, ylabelGap: 40,
      x: { cats },
      y: auc ? { lim: [0.55, 0.72], ticks: tks(range(0.55, 0.7, 0.05), 2), label: "AUC" } : { lim: [0, 0.3], ticks: tks(range(0, 0.3, 0.1), 1), label: "Spearman ρ" },
    });
    label(A.top, (A.x0 + A.x1) / 2, A.y0 - 28 * A.fs, t.detail, { "text-anchor": "middle", "font-size": 12 * A.fs, fill: "#666" });
    const F = t.floor;
    const vals = [F["ipSAE formula"], F["Linear regression"], F["MLP"]];
    const cols = [COL.published, COL.linear, COL.mlp];
    vals.forEach((v, i) => {
      const x = A.X(i), w = A.X(0.62) - A.X(0);
      el("rect", { x: x - w / 2, y: A.Y(v), width: w, height: A.Y(A.Y === null ? 0 : (auc ? 0.55 : 0)) - A.Y(v), fill: cols[i], stroke: "#333", "stroke-width": 0.5 }, A.data);
      label(A.top, x, A.Y(v) - 5, fmt(v, 3), { "text-anchor": "middle", "font-size": 10.5 * A.fs, fill: "#333" });
    });
    const arm = EFF.map(e => t.arms[e]).filter(v => v != null);
    const best = Math.max(...arm), x3 = A.X(3);
    el("line", { x1: x3, x2: x3, y1: A.Y(Math.min(...arm)), y2: A.Y(best), stroke: COL.opus, "stroke-width": 3, "stroke-opacity": 0.4, "stroke-linecap": "round" }, A.data);
    arm.forEach(v => el("circle", { cx: x3, cy: A.Y(v), r: 2.6, fill: COL.opus, "fill-opacity": 0.55 }, A.data));
    marker("o", x3, A.Y(best), COL.opus, A.data, 1.4);
    label(A.top, x3, A.Y(best) - 9, fmt(best, 3), { "text-anchor": "middle", "font-size": 10.5 * A.fs, fill: COL.opus, "font-weight": 600 });
    el("line", { x1: A.X(0) - 30, x2: A.x1, y1: A.Y(F["ipSAE formula"]), y2: A.Y(F["ipSAE formula"]), stroke: COL.published, "stroke-dasharray": "2 3", "stroke-width": 1 }, A.refs);
    return A;
  }

  function skempi(svg, o) {
    const p = o || {}, S = D().ipsae.skempi;
    const A = axes(svg, {
      W: p.W || 640, H: p.H || 300, fs: p.fs, title: p.title === undefined ? "Measured structures, mechanism held out" : p.title, m: { l: 62 }, ylabelGap: 48,
      x: effortAxis(), y: { lim: [0.1, 0.45], ticks: tks(range(0.1, 0.45, 0.05), 2), label: "Spearman ρ with measured p~K~_d" },
    });
    ref(A, S.floor["Buried area, unfitted"], "Buried area, no parameters", { left: true });
    ref(A, S.floor["Linear regression, fitted"], "Linear regression on sixty features", { left: true, below: true });
    ref(A, S.floor["MLP, fitted"], "MLP on sixty features", { left: true, below: true });
    series(A, { pts: effortPts(S.arms, v => ({ y: v })), color: COL.opus, width: 2.4, ms: 1.2 });
    legend(A, A.x1 - 8, A.y1 - 8, [{ text: "Rules derived by Claude Opus 5.5", color: COL.opus, marker: "o" }], { anchor: "right", valign: "bottom", fs: 0.9 });
    return A;
  }

  window.Charts = { COL, EFF, el, label, axes, legend, series, ref, marker, statement, edits, ladderCaps, ladderParams, gaps, cueBars, lengthPlot, scalePlot, imagine, digitRegimes, weights, initCurves, crossings, powerlaw, tabLadder, tabTask, ipsaeTest, skempi };
})();

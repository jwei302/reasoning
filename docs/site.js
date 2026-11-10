// Draws the figures of the project page and wires the tabbed ones. Every number comes from
// data.js; every chart builder lives in charts.js, which the companion site shares.
(function () {
  "use strict";
  const C = window.Charts;
  const $ = id => document.getElementById(id);

  // A tab bar inside a figure. items: {tab, desc}. select(i) draws.
  function tabs(fig, items, draw, descEl) {
    const bar = fig.querySelector(".tabs");
    if (!bar) return;
    const btns = items.map((it, i) => {
      const b = document.createElement("button");
      b.type = "button"; b.className = "tab"; b.setAttribute("role", "tab"); b.textContent = it.tab;
      b.addEventListener("click", () => sel(i));
      b.addEventListener("keydown", e => {
        if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
        const j = (i + (e.key === "ArrowRight" ? 1 : items.length - 1)) % items.length;
        sel(j); btns[j].focus(); e.preventDefault();
      });
      bar.appendChild(b);
      return b;
    });
    function sel(i) {
      btns.forEach((b, j) => { b.setAttribute("aria-selected", String(i === j)); b.tabIndex = i === j ? 0 : -1; });
      if (descEl) descEl.textContent = items[i].desc || "";
      draw(i);
    }
    sel(0);
  }

  /* ------------------------------------------------------------------ hero */
  const HERO = [
    { tab: "Digits", desc: "Every weight of these networks was chosen by reasoning. No optimizer, no copied weights, no stored examples.", draw: s => C.weights(s, { W: 700, H: 330 }) },
    { tab: "Tabular", desc: "Ten prediction tasks from six fields. Reasoned programs against tuned learned models on identical rows.", draw: s => C.tabLadder(s, { W: 700 }) },
    { tab: "Protein binding", desc: "Rules derived from a structure predictor's own error estimates, against the published interface score and two fitted models.", draw: s => C.ipsaeTest(s, 1, { W: 700, H: 330, title: "Detecting binders on a target never seen" }) },
  ];
  function hero() {
    const fig = $("hero"), svg = $("hero-plot");
    tabs(fig, HERO, i => HERO[i].draw(svg), $("hero-desc"));
  }

  /* ---------------------------------------------------------------- digits */
  function digits() {
    C.digitRegimes($("digits-astra"), "Astra", { W: 400, H: 330, legend: false });
    C.digitRegimes($("digits-opus"), "Opus", { W: 400, H: 330 });
    C.weights($("weights"), { W: 760, H: 340 });
    C.initCurves($("init-curves"), { W: 400, H: 320 });
    C.crossings($("init-cross"), { W: 400, H: 320 });
    C.powerlaw($("powerlaw"), { W: 760, H: 320 });
  }

  /* --------------------------------------------------------------- tabular */
  function tabular() {
    C.tabLadder($("tab-ladder"), { W: 760 });
    const T = window.DATA.tabular;
    tabs($("fig-tab-task"), T.map(t => ({ tab: t.label, desc: t.desc })), i => C.tabTask($("tab-task"), i, { W: 760, H: 330 }), $("tab-desc"));
  }

  /* ----------------------------------------------------------------- ipSAE */
  function ipsae() {
    window.DATA.ipsae.tests.forEach((t, i) => C.ipsaeTest($("ipsae-" + i), i, { W: 256, H: 330 }));
    C.skempi($("skempi"), { W: 760, H: 320 });
  }


  /* -------------------------------------------------- lightbox and BibTeX */
  function misc() {
    const box = $("lightbox"), big = box.querySelector("img");
    document.querySelectorAll("img.zoomable").forEach(img => img.addEventListener("click", () => {
      big.src = img.currentSrc || img.src; big.alt = img.alt; box.classList.add("open");
    }));
    box.addEventListener("click", () => box.classList.remove("open"));
    document.addEventListener("keydown", e => { if (e.key === "Escape") box.classList.remove("open"); });
    const copy = $("copy-bib");
    if (copy) copy.addEventListener("click", () => {
      const done = () => { copy.textContent = "Copied"; setTimeout(() => { copy.textContent = "Copy"; }, 1600); };
      if (navigator.clipboard) navigator.clipboard.writeText($("bibtex").textContent).then(done, () => {});
    });
  }

  /* ------------------------------------ outline: mark the section in view */
  function outline() {
    const links = [...document.querySelectorAll(".toc a")];
    const targets = links.map(a => document.querySelector(a.getAttribute("href")));
    const update = () => {
      const line = window.innerHeight * 0.3;
      let current = 0;
      targets.forEach((t, i) => { if (t && t.getBoundingClientRect().top <= line) current = i; });
      if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 2) current = links.length - 1;
      links.forEach((a, i) => a.classList.toggle("active", i === current));
    };
    window.addEventListener("scroll", update, { passive: true });
    update();
  }

  function start() {
    for (const fn of [outline, hero, digits, tabular, ipsae, misc]) {
      try { fn(); } catch (err) { console.error(err); }   // one broken figure should not take the others down
    }
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start); else start();
})();

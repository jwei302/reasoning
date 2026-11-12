// Page behaviour only. Every figure is a static SVG exported by poster/make_figs.py,
// so the page and the poster cannot drift apart.
(function () {
  "use strict";
  const $ = id => document.getElementById(id);

  /* ------------------------------------------- click a figure to enlarge it */
  function lightbox() {
    const box = $("lightbox");
    if (!box) return;
    const big = box.querySelector("img");
    document.querySelectorAll("img.zoomable").forEach(img => img.addEventListener("click", () => {
      big.src = img.currentSrc || img.src;
      big.alt = img.alt;
      box.classList.add("open");
    }));
    box.addEventListener("click", () => box.classList.remove("open"));
    document.addEventListener("keydown", e => { if (e.key === "Escape") box.classList.remove("open"); });
  }

  /* --------------------------------------------------------- copy the BibTeX */
  function bibtex() {
    const copy = $("copy-bib");
    if (!copy) return;
    copy.addEventListener("click", () => {
      const done = () => { copy.textContent = "Copied"; setTimeout(() => { copy.textContent = "Copy"; }, 1600); };
      if (navigator.clipboard) navigator.clipboard.writeText($("bibtex").textContent).then(done, () => {});
    });
  }

  /* ----------------------------------- mark the section currently in view */
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
    for (const fn of [outline, lightbox, bibtex]) {
      try { fn(); } catch (err) { console.error(err); }
    }
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start); else start();
})();

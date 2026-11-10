"""Poster figures, with type large enough to read at a distance.

Every value comes from docs/data.js, the same file the project page plots, so the poster and
the page can never disagree. Run from this folder:  python3 make_figs.py
"""
import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).parent
OUT = HERE / "figs"
SRC = HERE / "../docs/data.js"

ASTRA, OPUS, PUBLISHED = "#8669af", "#377f94", "#d97a1e"
GREY, LIGHT = "#8c8c8c", "#b5b5b5"
EFFORTS = ["low", "medium", "high", "xhigh", "max"]

mpl.rcParams.update({
    "font.family": "serif",
    "font.serif": ["DejaVu Serif"],
    "mathtext.fontset": "dejavuserif",
    "font.size": 19,
    "axes.titlesize": 21,
    "axes.labelsize": 19,
    "xtick.labelsize": 17,
    "ytick.labelsize": 17,
    "legend.fontsize": 16,
    "axes.linewidth": 1.1,
    "lines.linewidth": 2.6,
    "lines.markersize": 9,
    "xtick.direction": "out",
    "ytick.direction": "out",
    "figure.dpi": 110,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.04,
})


def load():
    text = SRC.read_text()
    return json.loads(text[text.index("=") + 1:].rstrip().rstrip(";"))


def grid(ax):
    ax.grid(True, color="#000000", alpha=0.08, linewidth=0.9)
    ax.set_axisbelow(True)


def save(fig, name):
    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / (name + ".pdf"))
    plt.close(fig)
    print("wrote", name)


# --------------------------------------------------------------- protein binding

def ipsae_tests(D):
    """The three held-out questions, each comparing the published score, two fitted models and reasoning."""
    tests = D["ipsae"]["tests"]
    fig, axes = plt.subplots(1, 3, figsize=(14.6, 5.9))
    for ax, t in zip(axes, tests):
        auc = t["metric"] == "AUC"
        floor, base = t["floor"], 0.55 if auc else 0.0
        bars = [("ipSAE", floor["ipSAE formula"], PUBLISHED),
                ("linear", floor["Linear regression"], GREY),
                ("MLP", floor["MLP"], LIGHT)]
        for i, (name, v, c) in enumerate(bars):
            ax.bar(i, v - base, bottom=base, width=0.66, color=c, edgecolor="#333", linewidth=0.8)
            ax.text(i, v + (0.004 if auc else 0.007), f"{v:.3f}", ha="center", va="bottom", fontsize=16)
        arms = [t["arms"][e] for e in EFFORTS if e in t["arms"]]
        best = max(arms)
        ax.plot([3, 3], [min(arms), best], color=OPUS, linewidth=5, alpha=0.4, solid_capstyle="round")
        ax.plot([3] * len(arms), arms, "o", color=OPUS, alpha=0.55, markersize=8)
        ax.plot([3], [best], "o", color=OPUS, markersize=15, markeredgecolor="white", markeredgewidth=1.4)
        ax.text(3, best + (0.006 if auc else 0.011), f"{best:.3f}", ha="center", va="bottom",
                fontsize=17, color=OPUS, fontweight="bold")
        ax.axhline(floor["ipSAE formula"], color=PUBLISHED, linestyle=(0, (2, 2)), linewidth=1.4)
        ax.set_xticks([])
        ax.set_xlim(-0.72, 3.72)
        ax.set_ylim(base, 0.72 if auc else 0.30)
        ax.set_ylabel("AUC" if auc else r"Spearman $\rho$")
        ax.set_title(f"{t['label']}\n{t['detail']}", fontsize=20, linespacing=1.3)
        grid(ax)
    handles = [plt.Rectangle((0, 0), 1, 1, facecolor=PUBLISHED, edgecolor="#333", label="ipSAE, published"),
               plt.Rectangle((0, 0), 1, 1, facecolor=GREY, edgecolor="#333", label="linear regression, fitted"),
               plt.Rectangle((0, 0), 1, 1, facecolor=LIGHT, edgecolor="#333", label="MLP, fitted"),
               plt.Line2D([], [], marker="o", color=OPUS, linewidth=5, alpha=0.6, label="derived by reasoning")]
    fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False, fontsize=18,
               bbox_to_anchor=(0.5, -0.015), handletextpad=0.6, columnspacing=2.0)
    fig.tight_layout(w_pad=1.6, rect=(0, 0.055, 1, 1))
    save(fig, "poster_ipsae")


def skempi(D):
    """Measured structures, one mechanism of association held out."""
    S = D["ipsae"]["skempi"]
    fig, ax = plt.subplots(figsize=(14.0, 5.3))
    ys = [S["arms"][e] for e in EFFORTS]
    for v, name, c, ls in [(S["floor"]["Buried area, unfitted"], "Buried area, no parameters", "#444", (0, (4, 3))),
                           (S["floor"]["Linear regression, fitted"], "Linear regression, 60 features", GREY, (0, (2, 2))),
                           (S["floor"]["MLP, fitted"], "MLP, 60 features", LIGHT, (0, (2, 2)))]:
        ax.axhline(v, color=c, linestyle=ls, linewidth=1.8)
        ax.text(4.42, v, name, ha="right", va="bottom", fontsize=15, color=c)
    ax.plot(range(5), ys, "-o", color=OPUS, markeredgecolor="white", markeredgewidth=1.2)
    ax.set_xticks(range(5)); ax.set_xticklabels(EFFORTS)
    ax.set_xlim(-0.35, 4.45)
    ax.set_ylim(0.12, 0.46)
    ax.set_xlabel("Reasoning effort")
    ax.set_ylabel(r"Spearman $\rho$ with measured p$K_\mathrm{d}$")
    ax.set_title("Measured structures, mechanism held out")
    grid(ax)
    save(fig, "poster_skempi")


# ------------------------------------------------------------------- other domains

def statement(D):
    """A theorem and its proof converge with model size, and edits do not separate them."""
    rows = D["mathematics"]["statement"]["families"]["Qwen3"]
    x = [r["params"] for r in rows]
    fig, axes = plt.subplots(1, 2, figsize=(13.4, 5.6))
    ax = axes[0]
    for key, name, c, m in [("matched", "Its own proof", "#1f77b4", "o"), ("mismatched", "Another proof", "#d62728", "s")]:
        y = [r[key] for r in rows]
        lo = [r[key + "_ci"][0] for r in rows]
        hi = [r[key + "_ci"][1] for r in rows]
        ax.plot(x, y, "-", color=c, marker=m, label=name, markeredgecolor="white", markeredgewidth=1.1)
        ax.fill_between(x, lo, hi, color=c, alpha=0.13)
    ax.axhline(D["mathematics"]["statement"]["tfidf"], color="#595959", linestyle=(0, (2, 3)), linewidth=1.4)
    ax.text(8, D["mathematics"]["statement"]["tfidf"] - 0.004, "word overlap floor", ha="right", va="top", fontsize=15, color="#595959")
    ax.set_title("Alignment rises with size")
    ax.legend(loc="upper left", frameon=True, framealpha=0.95)
    ax.set_ylim(0, 0.30)
    ax = axes[1]
    kinds = [("original", "original", "#1f77b4", "o"), ("rewrite", "true rewrite", "#ff7f0e", "s"),
             ("flip", "one inequality flipped", "#2ca02c", "^"), ("flip_all", "every inequality flipped", "#bcbd22", "D"),
             ("shuffle", "sentences shuffled", "#e377c2", "v")]
    for key, name, c, m in kinds:
        ax.plot(x, [r["edits"][key] for r in rows], "-", color=c, marker=m, label=name, linewidth=2.0,
                markeredgecolor="white", markeredgewidth=1.0)
    ax.set_title("Falsity does not separate them")
    ax.legend(loc="upper left", frameon=True, framealpha=0.95, fontsize=14)
    ax.set_ylim(0.15, 0.37)
    for ax in axes:
        ax.set_xscale("log")
        ax.set_xticks(x); ax.set_xticklabels([f"{v:g}B" for v in x])
        ax.minorticks_off()
        ax.set_xlabel("Parameters")
        ax.set_ylabel(r"Mutual $k$-NN alignment")
        grid(ax)
    fig.tight_layout(w_pad=2.0)
    save(fig, "poster_statement")


def cues(D):
    """A sensory cue moves a text-only model toward encoders of that sense."""
    M = D["touch"]["modes"]
    names = [("vision", "vision\n(DINOv2)"), ("touch:mae-base", "touch\n(MAE)"),
             ("touch:dino-base", "touch\n(DINO)"), ("touch:dinov2-base", "touch\n(DINOv2)")]
    fig, axes = plt.subplots(1, 2, figsize=(13.4, 5.4))
    for ax, (mode, title) in zip(axes, [("z_e", "Reading the prompt"), ("z_g", "After imagining the surface")]):
        for j, (cue, name, c) in enumerate([("none", "no cue", "#7f7f7f"), ("see", "see cue", "#1f77b4"), ("touch", "touch cue", "#d62728")]):
            ax.bar([i + (j - 1) * 0.26 for i in range(4)], [M[mode][k][cue] for k, _ in names],
                   width=0.25, color=c, edgecolor="#222", linewidth=0.6, label=name)
        ax.axvline(0.5, color="#000", alpha=0.25, linestyle=(0, (3, 3)))
        ax.set_xticks(range(4)); ax.set_xticklabels([n for _, n in names], fontsize=15)
        ax.set_ylim(0, 0.065)
        ax.set_ylabel(r"Mutual $k$-NN alignment")
        ax.set_title(title)
        grid(ax)
    axes[1].legend(loc="upper right", frameon=True, framealpha=0.95)
    fig.tight_layout(w_pad=2.0)
    save(fig, "poster_cues")


def digits(D):
    """Reasoned classifiers with full data, ten images and none, then networks with written weights."""
    R = D["digits"]["regimes"]
    refs = {r["label"]: r["accuracy"] for r in D["digits"]["references"]}
    fig, axes = plt.subplots(1, 2, figsize=(13.4, 5.6))
    ax = axes[0]
    for key, name, ls, m in [("full", "50,000 images", "-", "o"), ("ten", "ten images", (0, (5, 3)), "s"), ("none", "no images", (0, (2, 3)), "^")]:
        for fam, c in [("Astra", ASTRA), ("Opus", OPUS)]:
            xs = [i for i, e in enumerate(EFFORTS) if e in R[key][fam]]
            ys = [R[key][fam][EFFORTS[i]] for i in xs]
            ax.plot(xs, ys, linestyle=ls, marker=m, color=c, linewidth=2.1,
                    label=name if fam == "Astra" else None, markeredgecolor="white", markeredgewidth=1.0)
    ax.set_title("Classifying digits from a written theory")
    ax.set_ylim(70, 100)
    ax.legend(loc="lower right", frameon=True, framealpha=0.95, fontsize=15)
    ax = axes[1]
    for fam, c, name in [("Astra", ASTRA, "GPT-6 Astra"), ("Opus", OPUS, "Claude Opus 5.5")]:
        xs = [i for i, e in enumerate(EFFORTS) if e in R["weights"][fam]]
        ax.plot(xs, [R["weights"][fam][EFFORTS[i]] for i in xs], "-o", color=c, label=name,
                markeredgecolor="white", markeredgewidth=1.0)
    ax.set_title("Every weight written by reasoning")
    ax.set_ylim(78, 100)
    ax.legend(loc="lower right", frameon=True, framealpha=0.95, fontsize=15)
    for ax in axes:
        for label, name in [("linear classifier on pixels", "trained linear classifier"),
                            ("multilayer perceptron, 300 hidden", "trained MLP"),
                            ("convolutional network", "trained convolutional net")]:
            v = refs[label]
            ax.axhline(v, color="#595959", linestyle=(0, (2, 3)), linewidth=1.2)
            ax.text(4.35, v - 0.4, name, ha="right", va="top", fontsize=14, color="#595959")
        ax.set_xticks(range(5)); ax.set_xticklabels(EFFORTS)
        ax.set_xlim(-0.3, 4.4)
        ax.set_xlabel("Reasoning effort")
        ax.set_ylabel("Held-out accuracy (%)")
        grid(ax)
    fig.tight_layout(w_pad=2.0)
    save(fig, "poster_digits")


def powerlaw(D):
    """Error after gradient training against the effort that wrote the starting weights."""
    S = [s for s in D["digits"]["scaling"] if s["family"] == "Astra"]
    fig, ax = plt.subplots(figsize=(10.6, 5.8))
    r = np.linspace(1, 5, 120)
    for s in S:
        c, m, ls, name = (ASTRA, "o", "-", "from written weights") if s["condition"] == "authored" else (GREY, "s", (0, (4, 3)), "from random weights")
        ax.plot(r, 100 * s["A"] * r ** (-s["alpha"]), linestyle=ls, color=c, linewidth=2.2,
                label=f"{name}:  " + r"$e \propto r^{-%.2f}$" % s["alpha"])
        ax.plot([p["rank"] for p in s["points"]], [100 - p["accuracy"] for p in s["points"]], m,
                color=c, markersize=11, markeredgecolor="white", markeredgewidth=1.2)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xticks(range(1, 6)); ax.set_xticklabels(EFFORTS)
    ax.set_yticks([0.8, 1, 1.5, 2]); ax.set_yticklabels(["0.8", "1.0", "1.5", "2.0"])
    ax.minorticks_off()
    ax.set_xlabel("Effort that wrote the starting weights")
    ax.set_ylabel("Held-out error after training (%)")
    ax.set_title("Reasoning as initialization")
    ax.legend(loc="lower left", frameon=True, framealpha=0.95, fontsize=15)
    grid(ax)
    save(fig, "poster_powerlaw")


def tabular(D):
    """Ten tasks, each on its own scale, oriented so that right is better."""
    T = D["tabular"]
    fig, ax = plt.subplots(figsize=(14.6, 8.0))
    for i, t in enumerate(T):
        y = len(T) - 1 - i
        vals = list(t["learned"].values())
        means = {f: [q["mean"] for q in t["models"].get(f, [])] for f in ("Astra", "Opus")}
        vals += means["Astra"] + means["Opus"]
        lo, hi = min(vals), max(vals)
        pad = (hi - lo) * 0.08
        lo, hi = lo - pad, hi + pad

        def S(v):
            u = (v - lo) / (hi - lo)
            return u if t["higher"] else 1 - u
        if i % 2 == 0:
            ax.axhspan(y - 0.5, y + 0.5, color="#f6f6f3", zorder=0)
        ax.plot([0, 1], [y, y], color="#000", alpha=0.18, linewidth=1, zorder=1)
        for key, m in [("Linear", "|"), ("RandomForest", "s"), ("XGBoost", "^"), ("CatBoost", "D"), ("MLP", "v")]:
            if key in t["learned"]:
                ax.plot(S(t["learned"][key]), y, m, color=GREY, markersize=13 if m == "|" else 9,
                        markeredgewidth=2.4 if m == "|" else 0.8, zorder=2)
        for f, c, dy in [("Astra", ASTRA, 0.17), ("Opus", OPUS, -0.17)]:
            if not means[f]:
                continue
            xs = [S(v) for v in means[f]]
            ax.plot([min(xs), max(xs)], [y + dy] * 2, color=c, linewidth=5, alpha=0.45,
                    solid_capstyle="round", zorder=3)
            best = max(means[f]) if t["higher"] else min(means[f])
            ax.plot(S(best), y + dy, "o", color=c, markersize=11, markeredgecolor="white",
                    markeredgewidth=1.2, zorder=4)
        ax.text(-0.025, y, t["label"], ha="right", va="center", fontsize=18, fontweight="bold")
        ax.text(1.025, y, t["domain"], ha="left", va="center", fontsize=15, color="#666")
    ax.set_xlim(-0.30, 1.22)
    ax.set_ylim(-0.75, len(T) - 0.25)
    ax.set_yticks([])
    ax.set_xticks([])
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(False)
    ax.text(0, len(T) - 0.45, "worse", ha="left", va="bottom", fontsize=16, color="#666")
    ax.text(1, len(T) - 0.45, "better →", ha="right", va="bottom", fontsize=16, color="#666")
    handles = [plt.Line2D([], [], marker="|", color=GREY, linestyle="none", markersize=13, markeredgewidth=2.4, label="linear"),
               plt.Line2D([], [], marker="s", color=GREY, linestyle="none", label="random forest"),
               plt.Line2D([], [], marker="^", color=GREY, linestyle="none", label="XGBoost"),
               plt.Line2D([], [], marker="D", color=GREY, linestyle="none", label="CatBoost"),
               plt.Line2D([], [], marker="v", color=GREY, linestyle="none", label="MLP"),
               plt.Line2D([], [], marker="o", color=ASTRA, linewidth=5, alpha=0.6, label="GPT-6 Astra"),
               plt.Line2D([], [], marker="o", color=OPUS, linewidth=5, alpha=0.6, label="Claude Opus 5.5")]
    ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.45, -0.10), ncol=4,
              frameon=False, fontsize=15, handletextpad=0.5, columnspacing=1.4)
    save(fig, "poster_tabular")


def main():
    D = load()
    ipsae_tests(D)
    skempi(D)
    statement(D)
    cues(D)
    digits(D)
    powerlaw(D)
    tabular(D)


if __name__ == "__main__":
    main()

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
    """How much training data the theory needed, and what trained models get."""
    R = D["digits"]["regimes"]
    refs = {r["label"]: r["accuracy"] for r in D["digits"]["references"]}
    fig, axes = plt.subplots(1, 2, figsize=(13.4, 6.2),
                             gridspec_kw={"width_ratios": [2.15, 1]})

    ax = axes[0]
    groups = [("full", "50,000\nimages"), ("ten", "ten\nimages"), ("none", "no\nimages")]
    for j, (fam, c, name) in enumerate([("Astra", ASTRA, "GPT-6 Astra"), ("Opus", OPUS, "Claude Opus 5.5")]):
        ys = [max(R[k][fam].values()) for k, _ in groups]
        xs = [i + (j - 0.5) * 0.38 for i in range(len(groups))]
        ax.bar(xs, ys, width=0.36, color=c, edgecolor="white", linewidth=1.2, label=name, zorder=3)
        for x, y in zip(xs, ys):
            ax.text(x, y + 0.7, f"{y:.0f}", ha="center", va="bottom", fontsize=19,
                    fontweight="bold", color=c, zorder=4)
    ax.set_xticks(range(len(groups)))
    ax.set_xticklabels([n for _, n in groups], fontsize=19)
    ax.set_xlabel("Training images the model was shown", labelpad=10)
    ax.set_title("Accuracy of a written theory")
    ax.set_xlim(-0.62, 3.25)
    ax.legend(loc="lower left", frameon=True, framealpha=0.96, fontsize=16)

    ax = axes[1]
    ys = [max(R["weights"][f].values()) for f in ("Astra", "Opus")]
    ax.bar([0, 1], ys, width=0.56, color=[ASTRA, OPUS], edgecolor="white", linewidth=1.2, zorder=3)
    for x, y, c in zip([0, 1], ys, [ASTRA, OPUS]):
        ax.text(x, y + 0.7, f"{y:.0f}", ha="center", va="bottom", fontsize=19,
                fontweight="bold", color=c, zorder=4)
    ax.set_xticks([0, 1]); ax.set_xticklabels(["Astra", "Opus"], fontsize=19)
    ax.set_xlabel("No optimizer", labelpad=10)
    ax.set_title("Every weight written by hand")
    ax.set_xlim(-0.62, 1.62)

    for ax in axes:
        for label, name in [("linear classifier on pixels", "trained linear"),
                            ("multilayer perceptron, 300 hidden", "trained MLP")]:
            v = refs[label]
            ax.axhline(v, color="#444", linestyle=(0, (5, 4)), linewidth=1.8, zorder=2)
            ax.text(ax.get_xlim()[1] - 0.06, v + 0.6, name,
                    ha="right", va="bottom", fontsize=15, color="#444", zorder=4)
        ax.set_ylim(60, 103)
        ax.set_yticks([60, 70, 80, 90, 100])
        ax.set_ylabel("Held-out accuracy (%)")
        ax.grid(True, axis="y", color="#000000", alpha=0.08, linewidth=0.9)
        ax.set_axisbelow(True)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
    fig.tight_layout(w_pad=2.4)
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
    """Where the reasoned theory places among the five tuned models, on each task."""
    T = D["tabular"]
    rows = []
    for t in T:
        means = [q["mean"] for f in ("Astra", "Opus") for q in t["models"].get(f, [])]
        if not means:
            continue
        best = max(means) if t["higher"] else min(means)
        scored = sorted(list(t["learned"].items()) + [("__ours__", best)],
                        key=lambda kv: -kv[1] if t["higher"] else kv[1])
        names = [k for k, _ in scored]
        rows.append((t["label"], t["domain"], names.index("__ours__") + 1,
                     "classification" if t["higher"] else "regression"))
    rows.sort(key=lambda r: (r[2], r[0]))

    fig, ax = plt.subplots(figsize=(14.6, 7.8))
    for i, (label, domain, rank, kind) in enumerate(rows):
        y = len(rows) - 1 - i
        ax.plot([1, 6], [y, y], color="#000", alpha=0.13, linewidth=1.6, zorder=1)
        for r in range(1, 7):
            if r != rank:
                ax.plot(r, y, "o", color="#c9c9c9", markersize=13, zorder=2)
        c = OPUS if rank <= 3 else "#b4654a"
        ax.plot(rank, y, "o", color=c, markersize=27, markeredgecolor="white",
                markeredgewidth=2.0, zorder=4)
        ax.text(rank, y, str(rank), ha="center", va="center", fontsize=16,
                color="white", fontweight="bold", zorder=5)
        ax.text(0.72, y, label, ha="right", va="center", fontsize=19)
        ax.text(6.30, y, f"{domain}, {kind}", ha="left", va="center", fontsize=15, color="#777")

    ax.set_xticks(range(1, 7))
    ax.set_xticklabels(["1st", "2nd", "3rd", "4th", "5th", "6th"], fontsize=18)
    ax.set_xlim(0.55, 6.45)
    ax.set_ylim(-0.75, len(rows) - 0.25)
    ax.set_yticks([])
    ax.set_xlabel("Place of the reasoned theory among the five tuned models", labelpad=12)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.tick_params(axis="x", length=0)
    save(fig, "poster_tabular")

def framework(D):
    """Two lanes, identical splits, one frozen score. Orthogonal routing, nothing crosses."""
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
    from matplotlib.path import Path as MPath
    from matplotlib.patches import PathPatch

    YALE, GREY = "#00356B", "#9a9a9a"
    fig, ax = plt.subplots(figsize=(14.6, 6.0))
    ax.set_xlim(0, 100); ax.set_ylim(-2, 48); ax.axis("off")

    def box(x0, x1, y0, y1, lines, fc, ec, tc, fs=17, bold=False):
        ax.add_patch(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0,
                                    boxstyle="round,pad=0,rounding_size=1.4",
                                    facecolor=fc, edgecolor=ec, linewidth=2.0, zorder=3))
        ax.text((x0 + x1) / 2, (y0 + y1) / 2, lines, ha="center", va="center",
                fontsize=fs, color=tc, zorder=4, linespacing=1.45,
                fontweight="bold" if bold else "normal")

    def elbow(pts, c):
        """Orthogonal polyline with a single arrowhead at the end."""
        verts = list(pts)
        ax.add_patch(PathPatch(MPath(verts, [MPath.MOVETO] + [MPath.LINETO] * (len(verts) - 1)),
                               facecolor="none", edgecolor=c, linewidth=2.2,
                               joinstyle="round", capstyle="round", zorder=2))
        ax.add_patch(FancyArrowPatch(verts[-2], verts[-1], arrowstyle="-|>",
                                     mutation_scale=24, linewidth=0, color=c, zorder=2))

    # ---- shared splits
    box(2, 17, 16, 30, "Train\nValidation\nTest", "#EDF3F8", YALE, YALE, 18, bold=True)
    ax.text(9.5, 31.4, "Identical splits", ha="center", fontsize=16, color="#536272")

    # ---- deep learning lane
    ax.text(25, 44.6, "Deep learning", ha="left", fontsize=19, color=GREY, fontweight="bold")
    box(25, 47, 33, 43, "Fit parameters\nto the labels", "#f4f4f4", GREY, "#555")
    box(52, 74, 33, 43, "A predictor\nnobody can read", "#f4f4f4", GREY, "#555")
    elbow([(17, 23), (21, 23), (21, 38), (24.4, 38)], GREY)
    elbow([(47, 38), (51.4, 38)], GREY)

    # ---- reasoning lane
    ax.text(25, 13.2, "This work", ha="left", fontsize=19, color=YALE, fontweight="bold")
    box(25, 47, 1, 11, "State an explicit\ntheory of the data", "#EDF3F8", YALE, YALE)
    box(52, 74, 1, 11, "Write the theory\nas code", "#EDF3F8", YALE, YALE)
    elbow([(17, 23), (21, 23), (21, 6), (24.4, 6)], YALE)
    elbow([(47, 6), (51.4, 6)], YALE)

    # ---- revision loop, routed in the clear band between the lanes
    elbow([(63, 11), (63, 17), (41, 17), (41, 12.6)], YALE)
    ax.text(52, 18.4, "revise where validation predictions fail",
            ha="center", fontsize=16, color=YALE)

    # ---- one frozen score
    box(81, 98, 16, 30, "Scored once,\nfrozen, on the\nheld-out test set", "white", "#202A35",
        "#202A35", 18, bold=True)
    elbow([(74, 38), (77.5, 38), (77.5, 23), (80.4, 23)], GREY)
    elbow([(74, 6), (77.5, 6), (77.5, 23), (80.4, 23)], YALE)

    fig.tight_layout(pad=0.1)
    save(fig, "poster_framework")


def effort(D):
    """Every arm in the project on one axis: does more reasoning make a better theory?"""
    E = EFFORTS
    arms = []

    def add(dom, vals, higher):
        pts = [(i, v) for i, v in enumerate(vals) if v is not None]
        if len(pts) >= 4:
            arms.append((dom, pts, higher))

    for reg, fams in D["digits"]["regimes"].items():
        for f, d in fams.items():
            add("Digits", [d.get(e) for e in E], True)
    for x in D["tabular"]:
        for f in ("Astra", "Opus"):
            m = {q["effort"]: q["mean"] for q in x["models"].get(f, [])}
            add("Tabular", [m.get(e) for e in E], x["higher"])
    for t in D["ipsae"]["tests"]:
        add("Protein", [t["arms"].get(e) for e in E], True)
    add("Protein", [D["ipsae"]["skempi"]["arms"].get(e) for e in E], True)

    COL = {"Digits": ASTRA, "Tabular": OPUS, "Protein": PUBLISHED}
    norm = {k: np.full((0, 5), np.nan) for k in COL}
    series = {k: [] for k in COL}
    for dom, pts, hi in arms:
        idx = np.array([q[0] for q in pts])
        v = np.array([q[1] for q in pts], float)
        v = v if hi else -v
        row = np.full(5, np.nan)
        row[idx] = (v - v.min()) / (v.max() - v.min())
        series[dom].append(row)

    fig, ax = plt.subplots(figsize=(14.6, 6.2))
    x = np.arange(5)
    allR = np.vstack([np.vstack(v) for v in series.values()])
    q1 = np.nanpercentile(allR, 25, axis=0)
    q3 = np.nanpercentile(allR, 75, axis=0)
    ax.fill_between(x, q1, q3, color="#202A35", alpha=0.08, zorder=1, linewidth=0)
    ax.plot(x, np.nanmean(allR, axis=0), "-", color="#202A35", linewidth=5.0, zorder=5,
            label="All 32 arms")

    for dom in ("Digits", "Tabular", "Protein"):
        R = np.vstack(series[dom])
        ax.plot(x, np.nanmean(R, axis=0), "-o", color=COL[dom], linewidth=3.0, markersize=12,
                markeredgecolor="white", markeredgewidth=1.5, zorder=4,
                label=f"{dom} ({len(series[dom])})")

    ax.set_xticks(x); ax.set_xticklabels(E, fontsize=19)
    ax.set_xlim(-0.12, 4.12)
    ax.set_ylim(0.15, 0.88)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8])
    ax.set_yticklabels(["worse", "", "", "better"], fontsize=18)
    ax.set_xlabel("Reasoning effort", labelpad=10)
    ax.set_ylabel("Score within its own arm", labelpad=10)
    ax.set_title("More reasoning, better theories")
    ax.legend(loc="lower right", frameon=True, framealpha=0.96, fontsize=16, ncol=2)
    ax.grid(True, axis="y", color="#000000", alpha=0.08, linewidth=0.9)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    fig.tight_layout(pad=0.3)
    save(fig, "poster_effort")


def main():
    D = load()
    framework(D)
    effort(D)
    ipsae_tests(D)
    skempi(D)
    digits(D)
    powerlaw(D)
    tabular(D)


if __name__ == "__main__":
    main()

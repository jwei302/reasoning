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
    tests = tests[1:]
    fig, axes = plt.subplots(1, 2, figsize=(14.6, 5.2))
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
    fig, axes = plt.subplots(1, 2, figsize=(14.6, 6.8),
                             gridspec_kw={"width_ratios": [2.15, 1]})

    ax = axes[0]
    groups = [("full", "50,000"), ("ten", "10"), ("none", "0")]
    for j, (fam, c, name) in enumerate([("Astra", ASTRA, "GPT-6 Astra"), ("Opus", OPUS, "Claude Opus 5.5")]):
        ys = [max(R[k][fam].values()) for k, _ in groups]
        xs = [i + (j - 0.5) * 0.38 for i in range(len(groups))]
        ax.bar(xs, ys, width=0.36, color=c, edgecolor="white", linewidth=1.2, label=name, zorder=3)
        for x, y in zip(xs, ys):
            ax.text(x, y + 0.7, f"{y:.0f}", ha="center", va="bottom", fontsize=19,
                    fontweight="bold", color=c, zorder=4)
    ax.set_xticks(range(len(groups)))
    ax.set_xticklabels([n for _, n in groups], fontsize=19)
    ax.set_xlabel("Number of training images", labelpad=10)
    ax.set_title("Accuracy of a written theory")
    ax.set_xlim(-0.60, 2.86)
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
        for label, name in [("linear classifier on pixels", "linear"),
                            ("multilayer perceptron, 300 hidden", "MLP"),
                            ("convolutional network", "CNN")]:
            v = refs[label]
            ax.axhline(v, color="#444", linestyle=(0, (5, 4)), linewidth=1.8, zorder=2)
            ax.text(ax.get_xlim()[1] - 0.06, v + 0.6, name,
                    ha="right", va="bottom", fontsize=15, color="#444", zorder=4)
        ax.set_ylim(72, 104)
        ax.set_yticks([75, 80, 85, 90, 95, 100])
        ax.set_ylabel("Held-out accuracy (%)")
        ax.grid(True, axis="y", color="#000000", alpha=0.08, linewidth=0.9)
        ax.set_axisbelow(True)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
    fig.tight_layout(w_pad=1.4)
    save(fig, "poster_digits")

def powerlaw(D):
    """Error after gradient training against the effort that wrote the starting weights."""
    S = [s for s in D["digits"]["scaling"] if s["family"] == "Astra"]
    fig, ax = plt.subplots(figsize=(14.6, 4.8))
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
    pass
    ax.legend(loc="lower left", frameon=True, framealpha=0.95, fontsize=15)
    grid(ax)
    save(fig, "poster_powerlaw")


def tabular(D):
    """Where the reasoned theory places among the five tuned models, compactly."""
    T = D["tabular"]
    rows = []
    for t in T:
        means = [q["mean"] for f in ("Astra", "Opus") for q in t["models"].get(f, [])]
        if not means:
            continue
        best = max(means) if t["higher"] else min(means)
        scored = sorted(list(t["learned"].items()) + [("__ours__", best)],
                        key=lambda kv: -kv[1] if t["higher"] else kv[1])
        rows.append((t["label"], [k for k, _ in scored].index("__ours__") + 1))
    rows.sort(key=lambda r: r[1])

    fig, ax = plt.subplots(figsize=(14.6, 5.0))
    for i, (label, rank) in enumerate(rows):
        ax.plot([i, i], [0.6, 6.4], color="#000", alpha=0.10, linewidth=1.4, zorder=1)
        for r in range(1, 7):
            if r != rank:
                ax.plot(i, r, "o", color="#cfcfcf", markersize=9, zorder=2)
        c = OPUS if rank <= 3 else "#b4654a"
        ax.plot(i, rank, "o", color=c, markersize=24, markeredgecolor="white",
                markeredgewidth=1.8, zorder=4)
        ax.text(i, rank, str(rank), ha="center", va="center", fontsize=15,
                color="white", fontweight="bold", zorder=5)
    ax.set_xticks(range(len(rows)))
    ax.set_xticklabels([r[0] for r in rows], rotation=38, ha="right", fontsize=17)
    ax.set_xlim(-0.6, len(rows) - 0.4)
    ax.invert_yaxis()
    ax.set_yticks([1, 2, 3, 4, 5, 6])
    ax.set_yticklabels(["1st", "2nd", "3rd", "4th", "5th", "6th"], fontsize=17)
    ax.set_ylim(6.6, 0.4)
    ax.set_ylabel("Place among the\nfive tuned models", fontsize=18)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.tick_params(length=0)
    fig.tight_layout(pad=0.3)
    save(fig, "poster_tabular")

def framework(D):
    """Horizontal: three splits across, two learners down, set large."""
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

    YALE, GREY = "#00356B", "#8c8c8c"
    fig, ax = plt.subplots(figsize=(14.6, 8.8))
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")

    cols = [(16, 42, "Train split"), (44, 70, "Validation split"), (72, 98, "Test split")]
    for x0, x1, name in cols:
        ax.text((x0 + x1) / 2, 94, name, ha="center", fontsize=30,
                color="#202A35", fontweight="bold")

    def row(y0, y1, label, cells, fc, ec, tc):
        ax.text(0, (y0 + y1) / 2, label, ha="left", va="center", fontsize=29,
                color=tc, fontweight="bold", linespacing=1.3)
        for (x0, x1, _), text in zip(cols, cells):
            ax.add_patch(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0,
                                        boxstyle="round,pad=0,rounding_size=1.8",
                                        facecolor=fc, edgecolor=ec, linewidth=3.0, zorder=3))
            ax.text((x0 + x1) / 2, (y0 + y1) / 2, text, ha="center", va="center",
                    fontsize=24, color=tc, zorder=4, linespacing=1.45)
        for a, b in zip(cols, cols[1:]):
            ax.add_patch(FancyArrowPatch((a[1] + 0.6, (y0 + y1) / 2), (b[0] - 0.6, (y0 + y1) / 2),
                                         arrowstyle="-|>", mutation_scale=34,
                                         linewidth=3.0, color=ec, zorder=2))

    row(56, 88, "Deep\nlearning",
        ["Fit parameters\nby gradient\ndescent",
         "Tune and select\nthe checkpoint",
         "Evaluate"],
        "#f4f4f4", GREY, "#555")

    row(4, 36, "This\nwork",
        ["State a theory,\nwrite it as code",
         "Read the errors,\nrevise the theory",
         "Evaluate"],
        "#EDF3F8", YALE, YALE)

    ax.add_patch(FancyArrowPatch((63, 36.6), (51, 36.6), arrowstyle="-|>", mutation_scale=32,
                                 linewidth=3.0, color=YALE, zorder=5,
                                 connectionstyle="arc3,rad=0.42"))
    ax.text(57, 46.5, "repeat", ha="center", fontsize=26, color=YALE)
    fig.tight_layout(pad=0.1)
    save(fig, "poster_framework")

def effort(D):
    """Every arm as points, with a fitted trend and the mean at each setting."""
    from scipy.optimize import curve_fit
    E = EFFORTS
    rows = []

    def add(v, hi):
        pts = [(k, q) for k, q in enumerate(v) if q is not None]
        if len(pts) < 4:
            return
        idx = np.array([q[0] for q in pts])
        val = np.array([q[1] for q in pts], float)
        val = val if hi else -val
        r = np.full(5, np.nan)
        r[idx] = (val - val.min()) / (val.max() - val.min())
        rows.append(r)

    for reg, fams in D["digits"]["regimes"].items():
        for f, d in fams.items():
            add([d.get(e) for e in E], True)
    for x in D["tabular"]:
        for f in ("Astra", "Opus"):
            m = {q["effort"]: q["mean"] for q in x["models"].get(f, [])}
            add([m.get(e) for e in E], x["higher"])
    for t in D["ipsae"]["tests"]:
        add([t["arms"].get(e) for e in E], True)
    add([D["ipsae"]["skempi"]["arms"].get(e) for e in E], True)

    R = np.vstack(rows)
    X = np.repeat(np.arange(5)[None, :], R.shape[0], 0)
    ok = ~np.isnan(R)
    x, y = X[ok], R[ok]

    def sat(r, a, b, tau):
        return a + b * (1 - np.exp(-r / tau))
    pr, _ = curve_fit(sat, x, y, p0=[0.3, 0.5, 1.5], maxfev=20000)

    fig, ax = plt.subplots(figsize=(14.6, 5.5))
    rng = np.random.default_rng(0)
    ax.plot(x + rng.uniform(-0.13, 0.13, x.size), y, "o", color="#8c8c8c", alpha=0.30,
            markersize=9, markeredgewidth=0, zorder=2)

    g = np.linspace(0, 4, 200)
    ax.plot(g, sat(g, *pr), "-", color="#202A35", linewidth=4.2, zorder=4, label="fitted trend")

    mu = np.nanmean(R, axis=0)
    n = np.sum(ok, axis=0)
    se = np.nanstd(R, axis=0, ddof=1) / np.sqrt(n)
    ax.errorbar(np.arange(5), mu, yerr=1.96 * se, fmt="o", color=OPUS, markersize=15,
                markeredgecolor="white", markeredgewidth=1.8, elinewidth=3.0, capsize=9,
                capthick=3.0, zorder=5, label="mean, 95% interval")

    ax.set_xticks(range(5)); ax.set_xticklabels(E, fontsize=19)
    ax.set_xlim(-0.35, 4.35)
    ax.set_ylim(-0.05, 1.05)
    ax.set_yticks([0, 0.5, 1.0]); ax.set_yticklabels(["worst", "", "best"], fontsize=18)
    ax.set_xlabel("Reasoning effort", labelpad=10)
    ax.set_ylabel("Score within its own arm", labelpad=10)
    pass
    ax.legend(loc="lower right", frameon=True, framealpha=0.96, fontsize=17)
    grid(ax)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    fig.tight_layout(pad=0.3)
    save(fig, "poster_effort")

def curves(D):
    """Training from written weights against training from random weights."""
    C = D["digits"]["curves"]["Astra"]
    fig, ax = plt.subplots(figsize=(14.0, 5.8))
    for cond, c, name in [("random", GREY, "from random weights"),
                          ("authored", ASTRA, "from written weights")]:
        runs = [np.array(C[cond][e], float) for e in EFFORTS if e in C[cond]]
        steps = runs[0][:, 0]
        M = np.vstack([r[:, 1] for r in runs])
        ax.fill_between(steps, M.min(axis=0), M.max(axis=0), color=c, alpha=0.16,
                        linewidth=0, zorder=2)
        ax.plot(steps, np.median(M, axis=0), "-", color=c, linewidth=4.2,
                label=name, zorder=4)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(300, 8600)
    ax.set_ylim(1.2, 24)
    ax.set_yticks([1.5, 2, 3, 5, 10, 20]); ax.set_yticklabels(["1.5", "2", "3", "5", "10", "20"])
    ax.set_xticks([400, 1000, 2000, 4000, 8000])
    ax.set_xticklabels(["400", "1k", "2k", "4k", "8k"])
    ax.minorticks_off()
    ax.set_xlabel("Gradient steps")
    ax.set_ylabel("Held-out error (%)")
    ax.set_title("Training from a written theory")
    ax.legend(loc="upper right", frameon=True, framealpha=0.96, fontsize=17)
    grid(ax)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    fig.tight_layout(pad=0.3)
    save(fig, "poster_curves")


def skempi_floors(D):
    """On measured structures, unfitted physics beats everything that was fitted."""
    S = D["ipsae"]["skempi"]
    rows = [("Reasoned theory", max(S["arms"].values()), OPUS),
            ("Buried area", S["floor"]["Buried area, unfitted"], "#4d4d4d"),
            ("Contact count", S["floor"]["Contact count, unfitted"], "#4d4d4d"),
            ("Hydrogen bonds", S["floor"]["Hydrogen bonds, unfitted"], "#4d4d4d"),
            ("Linear regression", S["floor"]["Linear regression, fitted"], "#bdbdbd"),
            ("MLP", S["floor"]["MLP, fitted"], "#bdbdbd")]
    rows.sort(key=lambda r: r[1])
    fig, ax = plt.subplots(figsize=(14.0, 6.0))
    for i, (name, v, c) in enumerate(rows):
        ax.barh(i, v, height=0.62, color=c, edgecolor="white", linewidth=1.1, zorder=3)
        ax.text(v + 0.006, i, f"{v:.3f}", va="center", ha="left", fontsize=18,
                fontweight="bold", color=c, zorder=4)
        ax.text(-0.008, i, name, va="center", ha="right", fontsize=19, zorder=4)
    ax.set_yticks([])
    ax.set_ylim(-0.7, len(rows) - 0.3)
    ax.set_xlim(0, 0.49)
    ax.set_xlabel(r"Spearman $\rho$ with measured p$K_\mathrm{d}$", labelpad=10)
    ax.set_title("Measured structures, mechanism held out")
    ax.text(0.47, 0.35, "fitted on\n60 features", ha="right", va="center",
            fontsize=16, color="#999", linespacing=1.3)
    ax.grid(True, axis="x", color="#000000", alpha=0.08, linewidth=0.9)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    fig.tight_layout(pad=0.3)
    save(fig, "poster_skempi_floors")



def effort_curves(D):
    """The four cleanest effort curves, each on its own native metric."""
    E = EFFORTS
    T = {x["label"]: x for x in D["tabular"]}

    def tab(label, fam):
        m = {q["effort"]: q["mean"] for q in T[label]["models"][fam]}
        return [m.get(e) for e in E]

    panels = [
        ("California housing", "RMSE", tab("California housing", "Astra"), ASTRA, False),
        ("Concrete strength", "RMSE (MPa)", tab("Concrete strength", "Astra"), ASTRA, False),
        ("Used Fiat 500", "RMSE (euro)", tab("Used Fiat 500", "Opus"), OPUS, False),
        ("Written weights, MNIST", "Accuracy (%)",
         [D["digits"]["regimes"]["weights"]["Astra"].get(e) for e in E], ASTRA, True),
    ]
    fig, axes = plt.subplots(1, 4, figsize=(14.6, 5.0))
    x = np.arange(5)
    for ax, (title, ylab, v, c, higher) in zip(axes, panels):
        m = np.array([q is not None for q in v])
        y = np.array([q if q is not None else np.nan for q in v], float)
        ax.plot(x[m], y[m], "-o", color=c, linewidth=3.4, markersize=11,
                markeredgecolor="white", markeredgewidth=1.5, zorder=3)
        lo, hi = np.nanmin(y), np.nanmax(y)
        pad = (hi - lo) * 0.22
        ax.set_ylim(lo - pad, hi + pad)
        ax.set_xticks(x)
        ax.set_xticklabels(["low", "", "high", "", "max"], fontsize=16)
        ax.set_xlim(-0.3, 4.3)
        ax.set_title(title, fontsize=19, pad=10)
        ax.set_ylabel(ylab, fontsize=17)
        ax.tick_params(axis="y", labelsize=15)
        grid(ax)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
    axes[0].text(0, 1.0, "", transform=axes[0].transAxes)
    fig.supxlabel("Reasoning effort", fontsize=19, y=0.02)
    fig.tight_layout(w_pad=2.2, rect=(0, 0.05, 1, 1))
    save(fig, "poster_effort_curves")



def cycles(D):
    """One digits session, cycle by cycle: a hypothesis, a measurement, a revision."""
    cyc = [2, 3, 4, 5, 7]
    val = [61.56, 76.31, 81.94, 85.15, 83.37]
    why = ["continuity and\nterminal strokes",
           "remove false\nseparator tolerance",
           "finer angular\nenclosure evidence",
           "make evidence\nnecessary",
           "bowl and closed-four\nevidence"]
    fig, ax = plt.subplots(figsize=(14.6, 6.2))
    x = np.arange(len(cyc))
    ax.plot(x[:4], val[:4], "-o", color=ASTRA, linewidth=3.6, markersize=14,
            markeredgecolor="white", markeredgewidth=1.8, zorder=4)
    ax.plot(x[3:], val[3:], "--o", color="#b4654a", linewidth=3.0, markersize=14,
            markeredgecolor="white", markeredgewidth=1.8, zorder=4)
    offs = [(0, 26), (0, 26), (0, 26), (-26, 20), (0, -52)]
    has = ["center", "center", "center", "right", "center"]
    for i, (v, w) in enumerate(zip(val, why)):
        ax.annotate(w, (i, v), textcoords="offset points", xytext=offs[i], ha=has[i],
                    fontsize=16, color="#536272", linespacing=1.35)
        if i < 4:
            ax.text(i, v - 2.4, f"{v:.1f}", ha="center", va="top", fontsize=18,
                    fontweight="bold", color=ASTRA)
        else:
            ax.text(i + 0.16, v, f"{v:.1f}", ha="left", va="center", fontsize=18,
                    fontweight="bold", color="#b4654a")
    ax.annotate("the theory predicted a gain,\nthe measurement refused it,\nand the change was withdrawn",
                (3.52, 90.6), ha="center", va="center",
                fontsize=16, color="#b4654a", linespacing=1.35)
    ax.set_xticks(x); ax.set_xticklabels([f"cycle {c}" for c in cyc], fontsize=18)
    ax.set_xlim(-0.45, 4.6)
    ax.set_ylim(55, 95)
    ax.set_ylabel("Validation accuracy (%)")
    ax.set_title("Stating a theory, measuring it, revising it")
    grid(ax)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    fig.tight_layout(pad=0.3)
    save(fig, "poster_cycles")


def main():
    D = load()
    framework(D)
    effort(D)
    cycles(D)
    effort_curves(D)
    curves(D)
    skempi_floors(D)
    ipsae_tests(D)
    skempi(D)
    digits(D)
    powerlaw(D)
    tabular(D)


if __name__ == "__main__":
    main()

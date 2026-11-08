"""Part 1 · WHAT: convergence experiments E1.1-E1.3 ("the world progressed, but unevenly")."""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from wdi.story.common import GREY, VN, VN_COLOR, _save, panel, wcv


SIGMA_VARS = ["life_exp", "enrol_primary", "gdp_pc", "fertility", "u5_mort", "internet"]


def e1_1_sigma(p=None, vars_=SIGMA_VARS, min_n=100):
    """E1.1 sigma-convergence: cross-country CV per year (years with > min_n reporting countries)."""
    p = panel() if p is None else p
    rows = []
    for v in vars_:
        for yr, g in p[p[v].notna()].groupby("Year"):
            if len(g) > min_n:
                rows.append({"indicator": v, "Year": yr, "n": len(g), "cv": wcv(g[v].to_numpy())})
    return pd.DataFrame(rows)


def e1_3_robustness(p=None, vars_=SIGMA_VARS, start=1990, end=2013):
    """E1.3: is E1.1 an artefact of the changing country set? Compare the CV change start->end for
    (a) all reporting countries, (b) a balanced panel (countries reporting both years), (c) population weights."""
    p = panel() if p is None else p
    rows = []
    for v in vars_:
        a, b = (p[(p.Year == y) & p[v].notna()].set_index("CountryCode") for y in (start, end))
        both = a.index.intersection(b.index)
        both = both[a.loc[both, "population"].notna() & b.loc[both, "population"].notna()]
        for name, s, e in [("all reporting", a, b), ("balanced panel", a.loc[both], b.loc[both])]:
            rows.append({"indicator": v, "version": name, "n_start": len(s), "n_end": len(e),
                         "cv_start": wcv(s[v].to_numpy()), "cv_end": wcv(e[v].to_numpy())})
        rows.append({"indicator": v, "version": "balanced, population-weighted", "n_start": len(both),
                     "n_end": len(both),
                     "cv_start": wcv(a.loc[both, v].to_numpy(), a.loc[both, "population"].to_numpy()),
                     "cv_end": wcv(b.loc[both, v].to_numpy(), b.loc[both, "population"].to_numpy())})
    d = pd.DataFrame(rows)
    d["change_%"] = 100 * (d.cv_end / d.cv_start - 1)
    d["direction"] = np.where(d["change_%"] < -5, "converging", np.where(d["change_%"] > 5, "diverging", "flat"))
    return d


BETA_VARS = {"gdp_pc": "log", "life_exp": "level", "enrol_primary": "level", "fertility": "level"}


def e1_2_beta(p=None, start=1990, end=2014):
    """E1.2 beta-convergence: annual change start->end regressed on the start level.
    GDP uses log growth (%/yr) on log10 level; the others use units/yr on the level. beta < 0 = catch-up."""
    p = panel() if p is None else p
    a = p[p.Year == start].set_index("CountryCode")
    rows, pts = [], []
    for v, kind in BETA_VARS.items():
        n = p[p[v].notna() & (p.Year <= end)].groupby("Year").size()
        last = n[n > 100].index.max()  # series end at different years (life expectancy: 2013)
        b = p[p.Year == last].set_index("CountryCode")
        d = pd.DataFrame({"x": a[v], "y1": b[v]}).dropna()
        if kind == "log":
            d = d[(d.x > 0) & (d.y1 > 0)]
            d["change"] = 100 * np.log(d.y1 / d.x) / (last - start)
            d["x"] = np.log10(d.x)
        else:
            d["change"] = (d.y1 - d.x) / (last - start)
        r = stats.linregress(d.x, d.change)
        t = stats.t.ppf(0.975, len(d) - 2)
        rows.append({"indicator": v, "period": f"{start}-{last}", "x": "log10 level" if kind == "log" else "level", "n": len(d),
                     "beta": r.slope, "ci_low": r.slope - t * r.stderr, "ci_high": r.slope + t * r.stderr,
                     "r": r.rvalue, "r2": r.rvalue ** 2, "p": r.pvalue,
                     "vn_change": d.change.get(VN, np.nan)})
        pts.append(d.assign(indicator=v).reset_index())
    return pd.DataFrame(rows), pd.concat(pts, ignore_index=True)



# figures
SIGMA_NAMES = {"life_exp": "Life expectancy", "enrol_primary": "Primary enrolment", "gdp_pc": "GDP per capita",
               "fertility": "Fertility", "u5_mort": "Under-5 mortality", "internet": "Internet users"}


def fig_sigma(d, r):
    fig, ax = plt.subplots(figsize=(9, 4.2))
    for v, g in d.groupby("indicator"):
        g = g.sort_values("Year")
        ax.plot(g.Year, g.cv / g.cv.iloc[0], lw=2.4 if v == "gdp_pc" else 1.6,
                color="black" if v == "gdp_pc" else None,
                label=f"{SIGMA_NAMES.get(v, v)} ({g.cv.iloc[0]:.2f} → {g.cv.iloc[-1]:.2f})")
    ax.axhline(1, color=GREY, lw=0.8, ls="--")
    ax.set(title="E1.1 σ-convergence: cross-country CV, first year = 1", ylabel="CV relative to first year")
    ax.legend(fontsize=8.5, frameon=False, loc="center left", bbox_to_anchor=(1.01, 0.5), title="CV first → last year",
              title_fontsize=8.5)
    _save(fig, "E1_1_sigma.png")


def fig_beta(pts, res):
    fig, axes = plt.subplots(1, 4, figsize=(13, 3.6))
    for ax, (v, g) in zip(axes, pts.groupby("indicator", sort=False)):
        r = res.set_index("indicator").loc[v]
        ax.scatter(g.x, g.change, s=10, color=GREY, alpha=0.7)
        xs = np.linspace(g.x.min(), g.x.max(), 2)
        ax.plot(xs, r.beta * xs + (g.change.mean() - r.beta * g.x.mean()), color="black", lw=1.2)
        if VN in set(g.CountryCode):
            vn = g[g.CountryCode == VN].iloc[0]
            ax.scatter(vn.x, vn.change, s=40, color=VN_COLOR, zorder=3)
            left = vn.x < (g.x.min() + g.x.max()) / 2
            ax.annotate("Vietnam", (vn.x, vn.change), color=VN_COLOR, fontsize=8, xytext=(10 if left else -10, 12),
                        textcoords="offset points", ha="left" if left else "right", fontweight="bold",
                        bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85),
                        arrowprops=dict(arrowstyle="-", color=VN_COLOR, lw=0.8))
        ax.set(title=f"{SIGMA_NAMES.get(v, v)}\nβ = {r.beta:.3g}, r = {r.r:.2f}", xlabel=f"1990 {r.x}",
               ylabel="change per year" if ax is axes[0] else "")
        ax.title.set_fontsize(9)
    _save(fig, "E1_2_beta.png")


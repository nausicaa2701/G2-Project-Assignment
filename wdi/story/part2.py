"""Part 2 · WHY: how much of development does income explain?

E2.1  r2_layers      R² per theme: Ridge on log GDP only, Ridge on all features, best of the 19 models.
E2.2  residuals      Out-of-fold residuals of the income-only model: who beats its income.
E2.3  fixed_effects  Income slope between countries vs within countries (two-way fixed effects, 1990-2014).

App variant: `python run_story.py --part 2` -> results/story/part2/ (used by Home and the Why tab).
Analysis variant: `python -m wdi.story E2.1 E2.2 E2.3` -> results/story/E2_*.csv.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.base import clone
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold

from wdi.models import ROOT, THEMES, Config, data_path, dataset, evaluate, load, pipeline
from wdi.story.common import GREY, VN, VN_COLOR, _save, panel
from wdi.story.common import PEERS as REPORT_PEERS

OUT = ROOT / "results" / "story" / "part2"  # apart from the analysis CSVs of `python -m wdi.story`

# Themes where "income explains X" makes sense (Economy's target *is* income).
STORY_THEMES = [t for t in THEMES if THEMES[t]["target"] != "gdp_pc"]
# +1: a higher value than income predicts is the "better" outcome; -1: lower is better.
GOOD_DIRECTION = {"Health": 1, "Education": 1, "Technology": 1, "Demography": -1, "Environment": -1}
UNITS = {"Health": "years", "Education": "pp of enrolment", "Technology": "users per 100",
         "Demography": "births per woman", "Environment": "× CO₂ per head"}
PEERS = ["VNM", "CHN", "THA", "IDN", "PHL"]


def _cfg(feature_set, seeds, folds, themes=None):
    return Config(themes=themes or STORY_THEMES, models=["Ridge"], seeds=list(seeds), folds=folds,
                  mode="snapshot", feature_set=feature_set)


# E2.1
def r2_layers(seeds=(0, 1, 2, 3, 4), folds=5, summary_path=ROOT / "results" / "summary_snapshot.csv"):
    """R² of income-only Ridge, all-feature Ridge, and the best zoo model (from run_models.py)."""
    rows = []
    for label, fs in (("income", "income_only"), ("all", "all")):
        m, _ = evaluate(_cfg(fs, seeds, folds))
        g = m.groupby("theme").r2.agg(["mean", "std"])
        rows += [{"theme": t, "layer": label, "model": "Ridge", "r2_mean": r["mean"], "r2_std": r["std"]}
                 for t, r in g.iterrows()]
    best = (pd.read_csv(summary_path).sort_values("r2_mean", ascending=False).groupby("theme").head(1))
    rows += [{"theme": r.theme, "layer": "best", "model": r.model, "r2_mean": r.r2_mean, "r2_std": r.r2_std}
             for r in best.itertuples() if r.theme in STORY_THEMES]
    out = pd.DataFrame(rows)
    out["target"] = out.theme.map(lambda t: THEMES[t]["target"])
    return out


def layer_table(layers):
    """Wide view: one row per theme with the increment each layer adds (for a stacked bar)."""
    w = layers.pivot(index="theme", columns="layer", values="r2_mean")[["income", "all", "best"]]
    w["best_model"] = layers[layers.layer == "best"].set_index("theme").model
    w["add_features"] = (w["all"] - w["income"]).clip(lower=0)
    w["add_complexity"] = (w["best"] - w[["income", "all"]].max(axis=1)).clip(lower=0)
    w["income_share"] = w["income"] / w["best"]
    return w.reset_index().sort_values("income", ascending=False)


# E2.2
def residuals(seeds=(0, 1, 2, 3, 4), folds=5):
    """Out-of-fold residuals of the income-only model for every country and theme.

    For log targets (CO₂) the residual is a ratio: 3.0 means three times what income predicts.
    `score` is the percentile in the *good* direction (100 = beats its income by the most).
    """
    _, oof = evaluate(_cfg("income_only", seeds, folds))
    frames = []
    for theme, d in oof.groupby("theme"):
        log = THEMES[theme]["log"]
        d = d.assign(lp=np.log10(d.pred.clip(lower=1e-3)) if log else d.pred)
        g = d.groupby(["CountryCode", "ShortName", "Region", "Income"], dropna=False).agg(
            actual=("actual", "first"), lp=("lp", "mean"), lp_std=("lp", "std")).reset_index()
        if log:
            g["expected"] = 10 ** g.lp
            g["gap"] = g.actual / g.expected                   # ratio
            signed = np.log10(g.gap)
        else:
            g["expected"] = g.lp
            g["gap"] = g.actual - g.expected                   # natural units
            signed = g.gap
        perf = signed * GOOD_DIRECTION[theme]
        g["score"] = perf.rank(pct=True) * 100
        g["rank"] = perf.rank(ascending=False, method="min").astype(int)
        g["n"] = len(g)
        g["theme"], g["target"], g["unit"] = theme, THEMES[theme]["target"], UNITS[theme]
        frames.append(g.drop(columns="lp"))
    return pd.concat(frames, ignore_index=True)


def income_fit(snap=None):
    """In-sample OLS of each target on log10 GDP per capita: slope per 10× income, R², n."""
    snap = snap if snap is not None else pd.read_csv(data_path("wdi_snapshot_2005_2014.csv"))
    rows = []
    for theme in STORY_THEMES:
        spec = THEMES[theme]
        d = snap[[spec["target"], "gdp_pc"]].dropna()
        x = np.log10(d.gdp_pc)
        y = np.log10(d[spec["target"]].clip(lower=1e-3)) if spec["log"] else d[spec["target"]]
        b, a = np.polyfit(x, y, 1)
        r2 = np.corrcoef(x, y)[0, 1] ** 2
        rows.append({"theme": theme, "target": spec["target"], "log_target": spec["log"], "slope_per_10x": b,
                     "intercept": a, "r2": r2, "n": len(d)})
    return pd.DataFrame(rows)


def scorecard(res, codes=PEERS):
    """One row per (country, theme) for the selected countries, in the order given."""
    s = res[res.CountryCode.isin(codes)].copy()
    s["order"] = s.CountryCode.map({c: i for i, c in enumerate(codes)})
    return s.sort_values(["order", "theme"]).drop(columns="order")


# E2.3
def _demean(df, cols, keys, tol=1e-10, max_iter=500):
    """Remove one or more sets of fixed effects by alternating projections (works on unbalanced panels)."""
    out = df[cols].astype(float).copy()
    for _ in range(max_iter):
        prev = out.copy()
        for k in keys:
            out -= out.groupby(df[k]).transform("mean")
        if (out - prev).abs().to_numpy().max() < tol:
            break
    return out


def _slope_cluster(x, y, groups):
    """OLS slope through the origin (data already demeaned) with country-clustered standard error."""
    x, y = np.asarray(x), np.asarray(y)
    sxx = (x ** 2).sum()
    b = (x * y).sum() / sxx
    e = y - b * x
    score = pd.Series(x * e).groupby(np.asarray(groups)).sum()
    g, n = len(score), len(x)
    se = np.sqrt((score ** 2).sum() / sxx ** 2 * g / (g - 1) * (n - 1) / (n - 2))
    return b, se


def fixed_effects(years=(1990, 2014)):
    """Income slope per 10× GDP for each target: between countries vs within countries.

    between  : regression of country means (the cross-country "richer" view, like the Preston curve)
    pooled   : all country-years, no fixed effects
    within   : country + year fixed effects ("getting richer", net of the global trend)
    Returns (slopes, year_effects); year effects come from the within model, relative to the first year.
    """
    p = pd.read_csv(data_path("wdi_panel_wide.csv"))
    p = p[p.Year.between(*years) & p.gdp_pc.gt(0)].copy()
    p["x"] = np.log10(p.gdp_pc)
    rows, years_out = [], []
    for theme in STORY_THEMES:
        spec = THEMES[theme]
        d = p[p[spec["target"]].notna()].copy()
        d["y"] = np.log10(d[spec["target"]].clip(lower=1e-3)) if spec["log"] else d[spec["target"]]
        d = d[d.groupby("CountryCode").Year.transform("size") >= 5]      # need a time series per country
        cm = d.groupby("CountryCode")[["x", "y"]].mean()
        b_between = np.polyfit(cm.x, cm.y, 1)[0]
        b_pooled, se_pooled = _slope_cluster(d.x - d.x.mean(), d.y - d.y.mean(), d.CountryCode)
        dm = _demean(d, ["x", "y"], ["CountryCode", "Year"])
        b_within, se_within = _slope_cluster(dm.x, dm.y, d.CountryCode)
        rows.append({"theme": theme, "target": spec["target"], "log_target": spec["log"],
                     "n_obs": len(d), "n_countries": d.CountryCode.nunique(),
                     "between": b_between, "pooled": b_pooled, "pooled_se": se_pooled,
                     "within": b_within, "within_se": se_within,
                     "within_lo": b_within - 1.96 * se_within, "within_hi": b_within + 1.96 * se_within})
        # Year effects given b_within: alternate country and year means of the income-adjusted outcome.
        r = d.assign(r=d.y - b_within * d.x)
        a = pd.Series(0.0, index=r.index)
        for _ in range(200):
            yr = (r.r - a).groupby(r.Year).transform("mean")
            a_new = (r.r - yr).groupby(r.CountryCode).transform("mean")
            if (a_new - a).abs().max() < 1e-10:
                break
            a = a_new
        ye = (r.r - a).groupby(r.Year).mean()
        years_out.append(pd.DataFrame({"theme": theme, "Year": ye.index, "effect": (ye - ye.iloc[0]).values}))
    return pd.DataFrame(rows), pd.concat(years_out, ignore_index=True)


# run all
def run(seeds=(0, 1, 2, 3, 4), folds=5, out=OUT, log=print):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    log("E2.1 R² layers ...")
    layers = r2_layers(seeds, folds)
    layers.to_csv(out / "E2_1_r2_layers.csv", index=False)
    log("E2.2 residuals ...")
    residuals(seeds, folds).to_csv(out / "E2_2_residuals.csv", index=False)
    income_fit().to_csv(out / "E2_2_income_fit.csv", index=False)
    log("E2.3 fixed effects ...")
    slopes, year_fx = fixed_effects()
    slopes.to_csv(out / "E2_3_fixed_effects.csv", index=False)
    year_fx.to_csv(out / "E2_3_year_effects.csv", index=False)
    return layers


# analysis variant
R2_THEMES = [t for t in THEMES if t != "Economy"]  # income-only makes no sense when income is the target


def _oof(X, y, groups, seed, folds=5, alpha=1.0):
    cfg = Config(mode="snapshot")
    est = pipeline(Ridge(alpha=alpha), cfg, seed)
    pred = np.empty_like(y, dtype=float)
    for tr, te in GroupKFold(folds, shuffle=True, random_state=seed).split(X, y, groups):
        pred[te] = clone(est).fit(X.iloc[tr], y[tr]).predict(X.iloc[te])
    return pred


def e2_1_r2_layers(seeds=(0, 1, 2, 3, 4)):
    """E2.1: R2 in three layers per theme: (1) Ridge on log GDP only, (2) Ridge on all features,
    (3) best model of the 19-model suite (results/summary_snapshot.csv). Same grouped folds per seed."""
    cfg, df = Config(mode="snapshot"), load("snapshot")
    best = pd.read_csv(ROOT / "results" / "summary_snapshot.csv").sort_values("r2_mean").groupby("theme").tail(1)
    rows = []
    for theme in R2_THEMES:
        X, y, g, _ = dataset(df, theme, cfg)
        for s in seeds:
            for layer, cols in [("income only", ["gdp_pc"]), ("all features", list(X.columns))]:
                pred = _oof(X[cols], y, g, s)
                rows.append({"theme": theme, "layer": layer, "seed": s, "n": len(y),
                             "r2": 1 - ((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum()})
    d = pd.DataFrame(rows).groupby(["theme", "layer"]).r2.agg(["mean", "std"]).unstack("layer")
    d.columns = [f"{b} {a}" for a, b in d.columns]
    b = best.set_index("theme")
    d["best model"], d["best mean"], d["best std"] = b.model, b.r2_mean, b.r2_std
    return d.reset_index()


def e2_2_residuals(seeds=(0, 1, 2, 3, 4), focus=(VN, *REPORT_PEERS)):
    """E2.2 residual scorecard: out-of-fold residual of the income-only model (mean over seeds),
    in the target's own units (ratio actual/predicted for log targets), with rank and percentile."""
    cfg, df = Config(mode="snapshot"), load("snapshot")
    out = []
    for theme in R2_THEMES:
        spec = THEMES[theme]
        X, y, g, meta = dataset(df, theme, cfg)
        pred = np.mean([_oof(X[["gdp_pc"]], y, g, s) for s in seeds], axis=0)
        if spec["log"]:
            resid, unit = 10 ** (y - pred), "x predicted"
            actual, predicted = 10 ** y, 10 ** pred
        else:
            resid, unit, actual, predicted = y - pred, "units", y, pred
        d = meta[["CountryCode", "ShortName"]].assign(theme=theme, target=spec["target"], actual=actual,
                                                      predicted=predicted, residual=resid, unit=unit)
        d["rank"] = d.residual.rank(ascending=False, method="min").astype(int)  # 1 = most above expectation
        d["of"] = len(d)
        d["percentile"] = 100 * d.residual.rank(pct=True)
        out.append(d)
    d = pd.concat(out, ignore_index=True)
    return d, d[d.CountryCode.isin(focus)].reset_index(drop=True)


def _demean2(v, c, t, iters=200, tol=1e-10):
    """Two-way within transformation (country + year) for an unbalanced panel by alternating projections."""
    v = v.astype(float).copy()
    for _ in range(iters):
        old = v.copy()
        v -= pd.Series(v).groupby(c).transform("mean").to_numpy()
        v -= pd.Series(v).groupby(t).transform("mean").to_numpy()
        if np.abs(v - old).max() < tol:
            break
    return v


def _ols_cluster(x, y, cl):
    """Slope of y on x (no intercept, data already demeaned) with country-clustered SE."""
    b = (x @ y) / (x @ x)
    e = y - b * x
    meat = pd.Series(x * e).groupby(cl).sum().pow(2).sum()
    G = len(np.unique(cl))
    se = np.sqrt(meat / (x @ x) ** 2 * G / (G - 1))
    return b, se


def e2_3_fixed_effects(years=(1990, 2014), y_var="life_exp"):
    """E2.3: life expectancy on log10 GDP per capita: between-country, pooled, and two-way fixed effects.
    The FE slope is the within-country association (what happens when a given country gets richer)."""
    p = panel()
    d = p[p.Year.between(*years)][["CountryCode", "Year", y_var, "gdp_pc"]].dropna()
    d = d[d.gdp_pc > 0].assign(lg=lambda x: np.log10(x.gdp_pc))
    rows = []
    m = d.groupby("CountryCode")[[y_var, "lg"]].mean()
    r = stats.linregress(m.lg, m[y_var])
    rows.append({"model": "Between countries (country means)", "slope_per_10x": r.slope, "se": r.stderr,
                 "n_obs": len(m), "n_countries": len(m)})
    r = stats.linregress(d.lg, d[y_var])
    b, se = _ols_cluster(d.lg.to_numpy() - d.lg.mean(), d[y_var].to_numpy() - d[y_var].mean(), d.CountryCode.to_numpy())
    rows.append({"model": "Pooled OLS", "slope_per_10x": b, "se": se, "n_obs": len(d),
                 "n_countries": d.CountryCode.nunique()})
    c, t = d.CountryCode.to_numpy(), d.Year.to_numpy()
    xw, yw = _demean2(d.lg.to_numpy(), c, t), _demean2(d[y_var].to_numpy(), c, t)
    b, se = _ols_cluster(xw, yw, c)
    rows.append({"model": "Two-way fixed effects (country + year)", "slope_per_10x": b, "se": se,
                 "n_obs": len(d), "n_countries": d.CountryCode.nunique()})
    yfe = d.assign(r=yw).groupby("Year")[y_var].mean()  # raw year means, for the common-shift remark
    out = pd.DataFrame(rows)
    out["ci_low"], out["ci_high"] = out.slope_per_10x - 1.96 * out.se, out.slope_per_10x + 1.96 * out.se
    return out, yfe



# figures (analysis variant)
def fig_r2(d):
    d = d.set_index("theme")
    inc = d["income only mean"]
    allf = (d["all features mean"] - inc).clip(lower=0)
    best = (d["best mean"] - d[["income only mean", "all features mean"]].max(axis=1)).clip(lower=0)
    fig, ax = plt.subplots(figsize=(8, 3.8))
    ax.barh(d.index, inc, color="#4a6fa5", label="income only (log GDP, Ridge)")
    ax.barh(d.index, allf, left=inc, color="#9bb7d4", label="+ all other indicators (Ridge)")
    ax.barh(d.index, best, left=inc + allf, color="#e0b04a", label="+ best of 19 models")
    for i, (t, r) in enumerate(d.iterrows()):
        ax.text(max(r["best mean"], r["all features mean"]) + 0.01, i, f"{r['best mean']:.2f}", va="center", fontsize=8)
    ax.set(xlim=(0, 1), xlabel="cross-validated R²", title="E2.1 How much does income explain? R² in three layers")
    ax.legend(fontsize=8, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=3)
    _save(fig, "E2_1_r2_layers.png")


def fig_residuals(full, focus):
    fig, ax = plt.subplots(figsize=(8.5, 4.2))
    themes = list(dict.fromkeys(full.theme))
    for i, t in enumerate(themes):
        g = full[full.theme == t]
        ax.scatter(g.percentile, np.full(len(g), i) + np.random.default_rng(0).uniform(-.15, .15, len(g)),
                   s=6, color=GREY, alpha=0.4)
        for _, r in focus[focus.theme == t].iterrows():
            vn = r.CountryCode == VN
            ax.scatter(r.percentile, i, s=60 if vn else 25, color=VN_COLOR if vn else "black", zorder=3,
                       marker="o" if vn else "|")
            if vn:
                lab = f"{r.residual:+.1f}" if r.unit == "units" else f"{r.residual:.1f}×"
                ha = "right" if r.percentile > 75 else "left" if r.percentile < 25 else "center"
                dx = {"right": -6, "left": 6, "center": 0}[ha]
                ax.annotate(f"VN {lab} (rank {r['rank']}/{r['of']})", (r.percentile, i), xytext=(dx, 9),
                            textcoords="offset points", ha=ha, fontsize=7.5, color=VN_COLOR, fontweight="bold",
                            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.9))
    ax.set_yticks(range(len(themes)), [f"{t}\n({THEMES[t]['target']})" for t in themes], fontsize=8)
    ax.set_ylim(-0.5, len(themes) - 0.25)
    ax.set(xlabel="percentile of residual vs income-only prediction (100 = most above expectation)", xlim=(-2, 104),
           title="E2.2 Residual scorecard: Vietnam (red) and peers CHN/THA/IDN/PHL/MYS (black ticks)")
    ax.title.set_fontsize(10)
    _save(fig, "E2_2_residuals.png")


def fig_fe(d):
    fig, ax = plt.subplots(figsize=(7, 2.8))
    ax.errorbar(d.slope_per_10x, range(len(d)), xerr=1.96 * d.se, fmt="o", color="black", capsize=4)
    ax.set_yticks(range(len(d)), d.model, fontsize=8)
    ax.axvline(0, color=GREY, lw=0.8)
    ax.set(xlabel="years of life expectancy per 10× GDP per capita (95% CI)",
           title="E2.3 Richer vs getting richer: between vs within-country slope")
    ax.title.set_fontsize(10)
    _save(fig, "E2_3_fixed_effects.png")


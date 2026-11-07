"""Part 2 · WHY: "Income explains most of development; the residual is the story."

E2.1  r2_layers        How much does income alone explain? R² in three layers per theme:
                       (1) Ridge on log GDP only, (2) Ridge on all features, (3) best of the 19-model zoo.
E2.2  residuals        Who does better or worse than their income predicts? Out-of-fold residuals of the
                       income-only model, in natural units, ranked across countries.
E2.3  fixed_effects    "Richer" vs "getting richer": the income slope between countries vs within a
                       country over time (two-way fixed effects, panel 1990-2014), plus year effects.

Everything reuses the pipeline in wdi/models.py (snapshot data, leak lists, grouped K-fold by country,
several seeds), so the numbers are directly comparable with results/summary_snapshot.csv.
"""
from pathlib import Path

import numpy as np
import pandas as pd

from wdi.models import THEMES, Config, data_path, evaluate

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results" / "story" / "part2"  # apart from the report CSVs of `python -m wdi.story`

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


# ---------------------------------------------------------------- E2.1
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


# ---------------------------------------------------------------- E2.2
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


# ---------------------------------------------------------------- E2.3
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


# ---------------------------------------------------------------- run all
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

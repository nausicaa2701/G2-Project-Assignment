"""Storyline experiments E1.1-E3.3 (docs/experiments.md) plus the missing-data / outlier checks of the report.

Run all:   python -m wdi.story            -> results/story/*.csv, figures/story/*.png
Run some:  python -m wdi.story E2.1 E2.2 --seeds 0 1 2 3 4
Every experiment is a function returning a DataFrame; `main` saves it and draws one figure.
"""
from itertools import combinations
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy import stats  # noqa: E402
from sklearn.base import clone  # noqa: E402
from sklearn.cluster import AgglomerativeClustering, KMeans  # noqa: E402
from sklearn.linear_model import Ridge  # noqa: E402
from sklearn.metrics import adjusted_rand_score  # noqa: E402
from sklearn.mixture import GaussianMixture  # noqa: E402
from sklearn.model_selection import GroupKFold  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402

from wdi.models import ROOT, THEMES, Config, data_path, dataset, load, pipeline  # noqa: E402

OUT, FIG = ROOT / "results" / "story", ROOT / "figures" / "story"
VN, VN_COLOR, GREY = "VNM", "#c0392b", "#9aa0a6"
PEERS = ["CHN", "THA", "IDN", "PHL", "MYS"]
INCOME_ORDER = ["Low income", "Lower middle income", "Upper middle income", "High income"]

# Same 15 indicators and preprocessing as the Clusters page of app.py.
CLUSTER_VARS = ["gdp_pc", "life_exp", "u5_mort", "fertility", "urban", "age65", "enrol_secondary", "internet",
                "mobile", "electricity", "co2_pc", "energy_pc", "safe_water", "forest", "trade_open"]
CLUSTER_LOG = ["gdp_pc", "u5_mort", "co2_pc", "energy_pc", "trade_open"]
CLUSTER_NAMES = {1: "Low development", 2: "Transition", 3: "Emerging", 4: "Advanced"}
# Social outcomes only (no income, no energy/CO2) for the "development twins" of E3.2.
SOCIAL_VARS = ["life_exp", "u5_mort", "fertility", "age65", "enrol_secondary", "internet", "mobile",
               "electricity", "safe_water", "urban"]


def panel():
    return pd.read_csv(data_path("wdi_panel_wide.csv"))


def snapshot():
    return pd.read_csv(data_path("wdi_snapshot_2005_2014.csv"))


def wcv(x, w=None):
    """Coefficient of variation std/mean, optionally weighted (population-weighted inequality)."""
    w = np.ones_like(x) if w is None else w
    m = np.average(x, weights=w)
    return np.sqrt(np.average((x - m) ** 2, weights=w)) / m


# ------------------------------------------------------------------ Part 1: WHAT
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


# ------------------------------------------------------------------ Part 2: WHY
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


def e2_2_residuals(seeds=(0, 1, 2, 3, 4), focus=(VN, *PEERS)):
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


# ------------------------------------------------------------------ Part 3: SO WHAT
def cluster_matrix(snap, vars_=CLUSTER_VARS, log_vars=CLUSTER_LOG, min_cov=0.7):
    """Countries with >= min_cov of vars_, log-transformed, income-group median imputed, standardised."""
    d = snap[["CountryCode", "ShortName", "Region", "Income"] + vars_]
    d = d[d[vars_].notna().mean(axis=1) >= min_cov].reset_index(drop=True)
    X = d[vars_].copy()
    for v in set(log_vars) & set(vars_):
        X[v] = np.log10(X[v].clip(lower=1e-2))
    X = X.fillna(X.groupby(d.Income, observed=True).transform("median")).fillna(X.median())
    return d, X, StandardScaler().fit_transform(X)


def fit_clusters(Z, gdp, algo="K-means", k=4, seed=42):
    """Cluster labels renumbered 1..k by the cluster's median GDP per capita (1 = poorest)."""
    if algo == "K-means":
        lab = KMeans(k, n_init=20, random_state=seed).fit_predict(Z)
    elif algo == "Gaussian mixture":
        lab = GaussianMixture(k, n_init=5, random_state=seed).fit(Z).predict(Z)
    else:
        lab = AgglomerativeClustering(k, linkage="ward").fit_predict(Z)
    order = pd.Series(np.asarray(gdp)).groupby(lab).median().rank(method="first").astype(int)
    return pd.Series(lab).map(order).to_numpy()


def income_agreement(lab, income):
    """Share of countries in the income group that dominates their cluster (as on the app's Clusters page)."""
    ct = pd.crosstab(lab, np.asarray(income))
    return ct.max(axis=1).sum() / len(lab)


def e3_1_cluster_robustness(seeds=range(20), k=4):
    """E3.1: 3 algorithms x 20 seeds. ARI vs the reference (K-means, seed 42, the app default), share of runs
    with Vietnam in the 'Emerging' cluster, and agreement with World Bank income groups."""
    snap = snapshot()
    d, X, Z = cluster_matrix(snap)
    ref = fit_clusters(Z, X.gdp_pc)
    vi = d.index[d.CountryCode == VN][0]
    rows, labs = [], {}
    for algo in ["K-means", "Gaussian mixture", "Agglomerative (Ward)"]:
        for s in seeds:
            lab = fit_clusters(Z, X.gdp_pc, algo, k, s)
            labs[(algo, s)] = lab
            rows.append({"algorithm": algo, "seed": s, "ari_vs_reference": adjusted_rand_score(ref, lab),
                         "vn_cluster": CLUSTER_NAMES.get(lab[vi], lab[vi]), "agreement": income_agreement(lab, d.Income)})
    runs = pd.DataFrame(rows)
    pair = {a: np.mean([adjusted_rand_score(labs[(a, i)], labs[(a, j)]) for i, j in combinations(seeds, 2)])
            for a in runs.algorithm.unique()}
    summ = runs.groupby("algorithm").agg(ari_vs_reference=("ari_vs_reference", "mean"),
                                         agreement=("agreement", "mean"),
                                         vn_emerging_share=("vn_cluster", lambda c: (c == "Emerging").mean()))
    summ["ari_between_seeds"] = pd.Series(pair)
    # how stable is each country's cluster across all 60 runs (share of runs in its modal cluster)
    allab = np.vstack(list(labs.values()))
    stab = pd.DataFrame({"CountryCode": d.CountryCode, "ShortName": d.ShortName,
                         "reference": pd.Series(ref).map(CLUSTER_NAMES),
                         "modal_share": [np.bincount(allab[:, i]).max() / len(allab) for i in range(len(d))]})
    return summ.reset_index(), runs, stab


def e3_2_twins(n=5, country=VN):
    """E3.2: nearest neighbours by GDP per capita alone vs by social outcomes only (no income in the space)."""
    snap = snapshot()
    d, X, Z = cluster_matrix(snap, SOCIAL_VARS, ["u5_mort"])
    i = d.index[d.CountryCode == country][0]
    gdp = np.log10(snap.set_index("CountryCode").loc[d.CountryCode, "gdp_pc"]).to_numpy()
    dist_soc = np.sqrt(((Z - Z[i]) ** 2).sum(axis=1))
    dist_gdp = np.abs(gdp - gdp[i])
    rows = []
    for space, dist in [("same income", dist_gdp), ("same social outcomes", dist_soc)]:
        order = [j for j in np.argsort(dist) if j != i and not np.isnan(dist[j])][:n]
        for r, j in enumerate(order, 1):
            rows.append({"space": space, "rank": r, "CountryCode": d.CountryCode[j], "country": d.ShortName[j],
                         "distance": dist[j], "gdp_pc": 10 ** gdp[j], "gdp_ratio_vs_vn": 10 ** (gdp[j] - gdp[i]),
                         "life_exp": snap.set_index("CountryCode").at[d.CountryCode[j], "life_exp"]})
    return pd.DataFrame(rows)


def e3_3_gaps(country=VN):
    """E3.3: Vietnam minus the median of the 'Emerging' and 'Advanced' clusters, per indicator, in raw units and
    in standard deviations of the (log-transformed where noted) indicator across countries."""
    snap = snapshot()
    d, X, Z = cluster_matrix(snap)
    lab = fit_clusters(Z, X.gdp_pc)
    i = d.index[d.CountryCode == country][0]
    raw = snap.set_index("CountryCode").loc[d.CountryCode, CLUSTER_VARS].reset_index(drop=True)
    rows = []
    for c in (3, 4):
        med_x, med_raw = X[lab == c].median(), raw[lab == c].median()
        for v in CLUSTER_VARS:
            rows.append({"versus": CLUSTER_NAMES[c], "indicator": v, "log": v in CLUSTER_LOG,
                         "vietnam": raw.at[i, v], "cluster_median": med_raw[v],
                         # no gap when Vietnam's own value was imputed (enrol_secondary is missing)
                         "gap_sd": (X.at[i, v] - med_x[v]) / X[v].std() if pd.notna(raw.at[i, v]) else np.nan})
    out = pd.DataFrame(rows)
    out["abs_gap_sd"] = out.gap_sd.abs()
    return out.sort_values(["versus", "abs_gap_sd"], ascending=[True, False]).reset_index(drop=True)


# ------------------------------------------------------------------ report checks (A2, A3)
def summary_stats(snap=None):
    """A2: summary statistics of every indicator in the 2005-2014 snapshot (one value per country)."""
    snap = snapshot() if snap is None else snap
    num = snap.drop(columns=["CountryCode", "ShortName", "Region", "Income"])
    s = num.describe().T
    s["missing_%"] = 100 * num.isna().mean()
    s["skew"] = num.skew()
    return s.rename(columns={"50%": "median"})[["count", "missing_%", "mean", "median", "std", "min", "max", "skew"]]


def missing_impact(snap=None, vars_=("gdp_pc", "life_exp", "u5_mort", "enrol_secondary", "internet",
                                     "co2_pc", "literacy", "poverty_190", "gini", "health_exp")):
    """A2 missing-data impact: is the reporting sample representative? Mean/median on reporters only vs
    after income-group median imputation, and coverage per income group."""
    snap = snapshot() if snap is None else snap
    rows = []
    for v in vars_:
        x = snap[v]
        imp = x.fillna(snap.groupby("Income")[v].transform("median"))
        cov = snap.groupby("Income")[v].apply(lambda s: 100 * s.notna().mean())
        rows.append({"indicator": v, "n": int(x.notna().sum()), "missing_%": 100 * x.isna().mean(),
                     "mean_reporters": x.mean(), "mean_imputed": imp.mean(),
                     "mean_shift_%": 100 * (imp.mean() / x.mean() - 1),
                     "median_reporters": x.median(), "median_imputed": imp.median(),
                     **{f"coverage {g}": cov.get(g, np.nan) for g in INCOME_ORDER}})
    return pd.DataFrame(rows)


def missing_corr_impact(snap=None, pairs=(("gdp_pc", "life_exp"), ("gdp_pc", "co2_pc"), ("gdp_pc", "literacy"),
                                          ("gdp_pc", "poverty_190"), ("gdp_pc", "gini"), ("life_exp", "health_exp"))):
    """A3 missing-data impact on exploration: Spearman rho on complete pairs vs after imputation, and on the
    'listwise' sample a multivariate analysis would keep if it required all 32 indicators."""
    snap = snapshot() if snap is None else snap
    num = snap.drop(columns=["CountryCode", "ShortName", "Region", "Income"])
    imp = num.fillna(num.groupby(snap.Income).transform("median"))
    rows = []
    for a, b in pairs:
        pw = num[[a, b]].dropna()
        rows.append({"pair": f"{a} ~ {b}", "n_pairwise": len(pw), "rho_pairwise": stats.spearmanr(pw[a], pw[b])[0],
                     "n_imputed": len(imp), "rho_imputed": stats.spearmanr(imp[a], imp[b])[0]})
    out = pd.DataFrame(rows)
    out.attrs["listwise_n_all32"] = int(num.dropna().shape[0])
    out.attrs["listwise_n_15cluster"] = int(snap[CLUSTER_VARS].dropna().shape[0])
    return out


def outliers(snap=None, top=3):
    """A3: IQR outliers (beyond 1.5 IQR, computed on log10 for skewed indicators) with the most extreme countries."""
    snap = snapshot() if snap is None else snap
    logv = {"gdp_pc", "gdp_pc_ppp", "population", "co2_pc", "energy_pc", "u5_mort", "infant_mort"}
    rows = []
    for v in snap.columns.drop(["CountryCode", "ShortName", "Region", "Income"]):
        x = snap.set_index("ShortName")[v].dropna()
        z = np.log10(x.clip(lower=1e-3)) if v in logv else x
        q1, q3 = z.quantile([0.25, 0.75])
        lo, hi = q1 - 1.5 * (q3 - q1), q3 + 1.5 * (q3 - q1)
        o = z[(z < lo) | (z > hi)]
        ext = (o - z.median()).abs().sort_values(ascending=False).index[:top]
        rows.append({"indicator": v, "scale": "log10" if v in logv else "raw", "n": len(z), "n_outliers": len(o),
                     "examples": ", ".join(f"{c} ({x[c]:,.3g})" for c in ext)})
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ figures
def _save(fig, name):
    FIG.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(FIG / name, dpi=150)
    plt.close(fig)


def fig_sigma(d, r):
    fig, ax = plt.subplots(figsize=(8, 4.2))
    for v, g in d.groupby("indicator"):
        g = g.sort_values("Year")
        ax.plot(g.Year, g.cv / g.cv.iloc[0], lw=2.4 if v == "gdp_pc" else 1.6,
                color="black" if v == "gdp_pc" else None, label=f"{v} ({g.cv.iloc[0]:.2f} → {g.cv.iloc[-1]:.2f})")
    ax.axhline(1, color=GREY, lw=0.8, ls="--")
    ax.set(title="E1.1 σ-convergence: cross-country CV, first year = 1", ylabel="CV relative to first year")
    ax.legend(fontsize=8, frameon=False)
    _save(fig, "E1_1_sigma.png")


def fig_beta(pts, res):
    fig, axes = plt.subplots(1, 4, figsize=(13, 3.4))
    for ax, (v, g) in zip(axes, pts.groupby("indicator", sort=False)):
        r = res.set_index("indicator").loc[v]
        ax.scatter(g.x, g.change, s=10, color=GREY, alpha=0.7)
        xs = np.linspace(g.x.min(), g.x.max(), 2)
        ax.plot(xs, r.beta * xs + (g.change.mean() - r.beta * g.x.mean()), color="black", lw=1.2)
        if VN in set(g.CountryCode):
            vn = g[g.CountryCode == VN].iloc[0]
            ax.scatter(vn.x, vn.change, s=40, color=VN_COLOR, zorder=3)
            ax.annotate("Vietnam", (vn.x, vn.change), color=VN_COLOR, fontsize=8, xytext=(4, 4), textcoords="offset points")
        ax.set(title=f"{v}: β={r.beta:.3g}, r={r.r:.2f}", xlabel=f"1990 {r.x}", ylabel="change per year")
        ax.title.set_fontsize(9)
    _save(fig, "E1_2_beta.png")


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
    fig, ax = plt.subplots(figsize=(8, 3.8))
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
                ax.annotate(f"VN {lab} (rank {r['rank']}/{r['of']})", (r.percentile, i), xytext=(0, 7),
                            textcoords="offset points", ha="center", fontsize=7.5, color=VN_COLOR)
    ax.set_yticks(range(len(themes)), [f"{t}\n({THEMES[t]['target']})" for t in themes], fontsize=8)
    ax.set(xlabel="percentile of residual vs income-only prediction (100 = most above expectation)", xlim=(0, 105),
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


def fig_clusters(summ):
    fig, ax = plt.subplots(figsize=(7.5, 3))
    x = np.arange(len(summ))
    for j, (c, lab) in enumerate([("ari_between_seeds", "ARI between seeds"), ("ari_vs_reference", "ARI vs reference"),
                                  ("agreement", "agreement with income groups"), ("vn_emerging_share", "Vietnam in 'Emerging'")]):
        ax.bar(x + (j - 1.5) * 0.2, summ[c], 0.2, label=lab, color=VN_COLOR if c.startswith("vn") else None)
    ax.set_xticks(x, summ.algorithm, fontsize=9)
    ax.set(ylim=(0, 1.05), title="E3.1 Cluster robustness over 20 seeds per algorithm")
    ax.legend(fontsize=7.5, frameon=False, ncol=2, loc="lower right")
    _save(fig, "E3_1_cluster_robustness.png")


def fig_gaps(d):
    g = d[d.versus == "Emerging"].sort_values("gap_sd")
    fig, ax = plt.subplots(figsize=(7, 4.4))
    ax.barh(g.indicator + np.where(g.log, " (log)", ""), g.gap_sd,
            color=[VN_COLOR if abs(v) >= 0.5 else GREY for v in g.gap_sd])
    ax.axvline(0, color="black", lw=0.8)
    ax.set(xlabel="Vietnam minus 'Emerging' cluster median, in SD", title="E3.3 Where Vietnam differs from its cluster")
    ax.title.set_fontsize(10)
    _save(fig, "E3_3_gaps.png")


def fig_missing(snap=None):
    snap = snapshot() if snap is None else snap
    num = snap.drop(columns=["CountryCode", "ShortName", "Region", "Income"])
    cov = 100 * num.notna().groupby(snap.Income).mean().reindex(INCOME_ORDER)
    cov = cov[cov.mean().sort_values().index]
    fig, ax = plt.subplots(figsize=(10, 3.2))
    im = ax.imshow(cov, aspect="auto", cmap="Blues", vmin=0, vmax=100)
    ax.set_xticks(range(cov.shape[1]), cov.columns, rotation=70, fontsize=7.5)
    ax.set_yticks(range(4), cov.index, fontsize=8)
    fig.colorbar(im, ax=ax, label="% of countries reporting", shrink=0.8)
    ax.set_title("Snapshot coverage by income group: poorer groups report less (missing not at random)", fontsize=10)
    _save(fig, "A2_missing_by_income.png")


# ------------------------------------------------------------------ CLI
def main(argv):
    seeds = [0, 1, 2, 3, 4]
    if "--seeds" in argv:
        k = argv.index("--seeds")
        seeds = [int(s) for s in argv[k + 1:]]
        argv = argv[:k]
    want = set(argv) or {"E1.1", "E1.2", "E1.3", "E2.1", "E2.2", "E2.3", "E3.1", "E3.2", "E3.3", "A2", "A3"}
    OUT.mkdir(parents=True, exist_ok=True)

    def save(d, name):
        d.to_csv(OUT / name, index=False)
        print(f"\n== {name}\n{d.head(30).to_string()}")

    if "E1.1" in want:
        d = e1_1_sigma()
        save(d, "E1_1_sigma.csv")
        fig_sigma(d, None)
    if "E1.2" in want:
        res, pts = e1_2_beta()
        save(res, "E1_2_beta.csv")
        fig_beta(pts, res)
    if "E1.3" in want:
        save(e1_3_robustness(), "E1_3_robustness.csv")
    if "E2.1" in want:
        d = e2_1_r2_layers(seeds)
        save(d, "E2_1_r2_layers.csv")
        fig_r2(d)
    if "E2.2" in want:
        full, focus = e2_2_residuals(seeds)
        full.to_csv(OUT / "E2_2_residuals_all.csv", index=False)
        save(focus, "E2_2_residuals_focus.csv")
        fig_residuals(full, focus)
    if "E2.3" in want:
        d, _ = e2_3_fixed_effects()
        save(d, "E2_3_fixed_effects.csv")
        fig_fe(d)
    if "E3.1" in want:
        summ, runs, stab = e3_1_cluster_robustness()
        runs.to_csv(OUT / "E3_1_runs.csv", index=False)
        stab.to_csv(OUT / "E3_1_country_stability.csv", index=False)
        save(summ, "E3_1_cluster_robustness.csv")
        fig_clusters(summ)
    if "E3.2" in want:
        save(e3_2_twins(), "E3_2_twins.csv")
    if "E3.3" in want:
        d = e3_3_gaps()
        save(d, "E3_3_gaps.csv")
        fig_gaps(d)
    if "A2" in want:
        save(summary_stats().reset_index(names="indicator"), "A2_summary_stats.csv")
        save(missing_impact(), "A2_missing_impact.csv")
        fig_missing()
    if "A3" in want:
        c = missing_corr_impact()
        save(c, "A3_missing_corr.csv")
        print("listwise n:", c.attrs)
        save(outliers(), "A3_outliers.csv")


if __name__ == "__main__":
    main(sys.argv[1:])

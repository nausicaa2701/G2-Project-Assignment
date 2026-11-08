"""A · Initial data exploration and B · Data preprocessing: the checks behind the two "Data" pages of the app
and of section 10 of the notebook.

A1  RAW_FILES, RAW_ATTRIBUTES, obs_per_year, coverage_by_decade     size and attributes
A2  summary_stats, missing_impact, fig_missing                      summary statistics + missing-value impact
A3  outliers, iqr_fences, hyperinflation, missing_corr_impact       outliers, correlated groups + missing impact
B   PIPELINE, validation, coverage_table, skew_transform,           what each preprocessing step did
    pca_variance, sample_sizes

The raw Kaggle files (574 MB) are not shipped with the app, so the raw-level numbers (RAW_FILES, the first
PIPELINE rows) are the logged output of the ETL in WDI_Analysis.ipynb; everything else is recomputed from
app_data/ (or data/processed/) on every call.
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.decomposition import PCA

from wdi.models import THEMES
from wdi.story.common import CLUSTER_VARS, INCOME_ORDER, _save, numeric, panel, snapshot

# ------------------------------------------------------------------ A1 · dataset overview
RAW_FILES = pd.DataFrame([
    ("Indicators.csv", "574 MB", 5_656_458, 6, "one value per country × indicator × year", "used"),
    ("Country.csv", "0.13 MB", 247, 31, "country metadata: region, income group, names", "used"),
    ("Series.csv", "3.3 MB", 1_345, 20, "indicator metadata: topic, definition, unit, source", "used"),
    ("Footnotes / CountryNotes / SeriesNotes", "56 MB", None, None, "free-text notes", "not used"),
    ("database.sqlite", "1.4 GB", None, None, "the same tables as the CSVs", "not used"),
], columns=["file", "size", "rows", "columns", "content", "status"])

RAW_ATTRIBUTES = pd.DataFrame([
    ("CountryCode / CountryName", "Indicators", "nominal (key)", "247 values: 214 economies + 33 aggregates"),
    ("IndicatorCode / IndicatorName", "Indicators", "nominal (key)", "1,344 values"),
    ("Year", "Indicators", "discrete numeric", "1960–2015"),
    ("Value", "Indicators", "continuous numeric", "meaning and unit depend on the indicator"),
    ("Region", "Country", "nominal", "7 regions; empty for aggregates"),
    ("IncomeGroup", "Country", "ordinal", "low < lower-middle < upper-middle < high (OECD / non-OECD)"),
    ("ShortName", "Country", "nominal", "display name"),
    ("Topic", "Series", "nominal", "91 topics, e.g. Health: Mortality"),
], columns=["attribute", "file", "type", "values"])

RAW_STRUCTURE = {"observations_by_year": {1960: 23_188, 1990: 117_634, 2010: 187_206, 2015: 14_762},
                 "economic_policy_series": 506}


def obs_per_year(p=None):
    """Non-empty indicator cells and reporting countries per year in the processed panel."""
    p = panel() if p is None else p
    num = numeric(p)
    return pd.DataFrame({"cells": num.notna().sum(axis=1), "country": p.CountryCode}).groupby(p.Year).agg(
        cells=("cells", "sum"), countries=("country", "nunique")).reset_index()


def coverage_by_decade(p=None):
    """% of country-years with a value, per indicator and decade (the notebook's coverage heatmap)."""
    p = panel() if p is None else p
    num = numeric(p)
    cov = 100 * num.notna().groupby((p.Year // 10 * 10).rename("decade")).mean()
    return cov.T.loc[cov.mean().sort_values(ascending=False).index]


# ------------------------------------------------------------------ A2 · summary statistics
def summary_stats(snap=None):
    """A2: summary statistics of every indicator in the 2005-2014 snapshot (one value per country)."""
    snap = snapshot() if snap is None else snap
    num = numeric(snap)
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
    num = numeric(snap)
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
    for v in numeric(snap).columns:
        x = snap.set_index("ShortName")[v].dropna()
        z = np.log10(x.clip(lower=1e-3)) if v in logv else x
        q1, q3 = z.quantile([0.25, 0.75])
        lo, hi = q1 - 1.5 * (q3 - q1), q3 + 1.5 * (q3 - q1)
        o = z[(z < lo) | (z > hi)]
        ext = (o - z.median()).abs().sort_values(ascending=False).index[:top]
        rows.append({"indicator": v, "scale": "log10" if v in logv else "raw", "n": len(z), "n_outliers": len(o),
                     "examples": ", ".join(f"{c} ({x[c]:,.3g})" for c in ext)})
    return pd.DataFrame(rows)



def fig_missing(snap=None):
    snap = snapshot() if snap is None else snap
    num = numeric(snap)
    cov = 100 * num.notna().groupby(snap.Income).mean().reindex(INCOME_ORDER)
    cov = cov[cov.mean().sort_values().index]
    fig, ax = plt.subplots(figsize=(10, 3.2))
    im = ax.imshow(cov, aspect="auto", cmap="Blues", vmin=0, vmax=100)
    ax.set_xticks(range(cov.shape[1]), cov.columns, rotation=70, fontsize=7.5)
    ax.set_yticks(range(4), cov.index, fontsize=8)
    fig.colorbar(im, ax=ax, label="% of countries reporting", shrink=0.8)
    ax.set_title("Snapshot coverage by income group: poorer groups report less (missing not at random)", fontsize=10)
    _save(fig, "A2_missing_by_income.png")



def iqr_fences(x, log=False):
    """(values on the analysis scale, lower fence, upper fence, outlier mask) for one indicator."""
    z = np.log10(x.clip(lower=1e-3)) if log else x
    q1, q3 = z.quantile([0.25, 0.75])
    lo, hi = q1 - 1.5 * (q3 - q1), q3 + 1.5 * (q3 - q1)
    return z, lo, hi, (z < lo) | (z > hi)


def hyperinflation(p=None, threshold=500):
    """Country-years with inflation above `threshold` %: flagged in cleaning, not deleted."""
    p = panel() if p is None else p
    h = p.loc[p.inflation > threshold, ["CountryCode", "ShortName", "Year", "inflation"]]
    return h.sort_values("inflation", ascending=False).reset_index(drop=True)


# ------------------------------------------------------------------ B · preprocessing
PIPELINE = pd.DataFrame([
    ("B4 Reduction", "chunked read of Indicators.csv, keep 32 of 1,344 indicators", "5,656,458 → 247,446 rows"),
    ("B1 Cleaning", "separate the 33 aggregates (empty Region)", "210,443 country rows kept, 37,003 set aside"),
    ("B1 Cleaning", "duplicates · non-finite · out-of-domain values", "0 · 0 · 0 found"),
    ("B1 Cleaning", "flag hyperinflation (> 500 %)", "29 country-years flagged, kept"),
    ("B2 Integration", "join Country.csv and Series.csv; merge the two high-income groups",
     "region, 4-level income group, names, topics"),
    ("B3 Transformation", "long → wide country-year panel", "11,935 country-years × 32 indicators"),
    ("B1 Cleaning", "linear interpolation of internal gaps ≤ 3 years, no extrapolation", "missing cells 44.9 % → 42.1 %"),
    ("B4 Reduction", "latest value per country in 2005–2014 (snapshot)", "214 countries × 32 indicators"),
    ("B4 Reduction", "coverage threshold", "exploration ≥ 60 % (31 kept), models ≥ 50 % (32 kept)"),
    ("B3 Transformation", "log₁₀ of skewed attributes, z-score standardisation", "near-symmetric, comparable scales"),
    ("B4 Reduction", "PCA on the 15 clustering indicators", "PC1 63.5 %, PC1 + PC2 70.8 %"),
], columns=["group", "step", "result"])

PCT_VARS = ["unemployment", "poverty_190", "urban", "age65", "age0_14", "female_lfp", "safe_water", "literacy",
            "forest", "renewables", "electricity"]          # bounded 0-100
SIGNED_VARS = ["gdp_growth", "inflation", "pop_growth"]       # may be negative; every other indicator is >= 0
INTERP_BEFORE = 44.9                                          # % missing before interpolation (notebook log)


def validation(p=None):
    """B1 data-quality checks on the processed panel: what was looked for, how many were found."""
    p = panel() if p is None else p
    num = numeric(p)
    nonneg = num.drop(columns=SIGNED_VARS)
    rows = [("duplicate (country, year) keys", int(p.duplicated(["CountryCode", "Year"]).sum()), "none to remove"),
            ("non-finite values (±inf)", int(np.isinf(num.to_numpy(dtype=float)).sum()), "none to remove"),
            ("percentages outside 0–100", int(((num[PCT_VARS] < 0) | (num[PCT_VARS] > 100)).sum().sum()),
             "none to remove"),
            ("negative values where impossible", int((nonneg < 0).sum().sum()), "none to remove"),
            ("aggregates left (empty Region)", int(p.Region.isna().sum()), "33 aggregates removed earlier"),
            ("hyperinflation years (> 500 %)", len(hyperinflation(p)), "flagged, kept; log-transformed in models"),
            ("missing cells after interpolation", f"{100 * num.isna().mean().mean():.1f} %",
             f"{INTERP_BEFORE} % before; the rest handled per method")]
    return pd.DataFrame(rows, columns=["check", "found", "action"])


def coverage_table(snap=None):
    """B1/B4 coverage threshold: % of countries reporting each indicator in the snapshot, and which rule keeps it."""
    snap = snapshot() if snap is None else snap
    cov = 100 * numeric(snap).notna().mean()
    d = cov.rename("coverage_%").sort_values().rename_axis("indicator").reset_index()
    d["exploration (≥ 60 %)"] = d["coverage_%"] >= 60
    d["models (≥ 50 %)"] = d["coverage_%"] >= 50
    return d


def skew_transform(snap=None, vars_=("gdp_pc", "gdp_pc_ppp", "population", "co2_pc", "energy_pc", "u5_mort",
                                     "infant_mort", "trade_open")):
    """B3: skewness and mean/median ratio before and after log10 for the right-skewed attributes."""
    snap = snapshot() if snap is None else snap
    rows = []
    for v in vars_:
        x = snap[v].dropna()
        lx = np.log10(x.clip(lower=1e-3))
        rows.append({"indicator": v, "skew_raw": stats.skew(x), "skew_log10": stats.skew(lx),
                     "mean/median raw": x.mean() / x.median(), "mean/median log10": 10 ** lx.mean() / x.median()})
    return pd.DataFrame(rows)


def pca_variance(snap=None):
    """B4: explained variance of PCA on the 15 standardised clustering indicators, plus PC1/PC2 loadings."""
    from wdi.story.part3 import cluster_matrix
    snap = snapshot() if snap is None else snap
    d, X, Z = cluster_matrix(snap)
    pca = PCA().fit(Z)
    var = pd.DataFrame({"component": [f"PC{i + 1}" for i in range(len(pca.explained_variance_ratio_))],
                        "explained_%": 100 * pca.explained_variance_ratio_})
    var["cumulative_%"] = var["explained_%"].cumsum()
    sign = np.sign(np.corrcoef(pca.transform(Z)[:, 0], X.gdp_pc)[0, 1])      # PC1 points towards richer
    load = pd.DataFrame({"indicator": CLUSTER_VARS, "PC1": sign * pca.components_[0], "PC2": pca.components_[1]})
    return var, load


def sample_sizes(snap=None):
    """Why we do not drop incomplete countries: rows kept under listwise deletion vs our per-method rules."""
    snap = snapshot() if snap is None else snap
    num = numeric(snap)
    rows = [("all 214 countries", len(snap), "starting point"),
            ("listwise: all 32 indicators", int(num.dropna().shape[0]), "drop any country with a gap"),
            ("listwise: 15 clustering indicators", int(snap[CLUSTER_VARS].dropna().shape[0]), "drop any gap"),
            ("ours: clustering (≥ 70 % of the 15, imputed)", int((snap[CLUSTER_VARS].notna().mean(axis=1) >= .7).sum()),
             "income-group median for the rest")]
    for t, spec in THEMES.items():
        rows.append((f"ours: model target {spec['target']}", int(snap[spec["target"]].notna().sum()),
                     "target observed; features imputed in-fold"))
    return pd.DataFrame(rows, columns=["sample", "countries", "rule"])

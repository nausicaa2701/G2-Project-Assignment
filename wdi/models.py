"""Multi-model, multi-seed evaluation of WDI indicators, one target per theme.

Reads the processed files written by WDI_Analysis.ipynb (data/processed/) and evaluates many
regressors with grouped cross-validation (a country never appears in both train and test fold).
Every run is configurable: seeds, folds, data mode, imputer, model list.
"""
from dataclasses import dataclass, field
from pathlib import Path
import warnings

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.compose import TransformedTargetRegressor
from sklearn.ensemble import (AdaBoostRegressor, ExtraTreesRegressor, GradientBoostingRegressor,
                              HistGradientBoostingRegressor, RandomForestRegressor,
                              StackingRegressor, VotingRegressor)
from sklearn.experimental import enable_iterative_imputer  # noqa: F401  (registers IterativeImputer)
from sklearn.impute import IterativeImputer, KNNImputer, SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import (BayesianRidge, ElasticNet, HuberRegressor, Lasso, LinearRegression,
                                  Ridge)
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold, GroupShuffleSplit
from sklearn.neighbors import KNeighborsRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)
try:  # optional boosters: registered only when installed
    from xgboost import XGBRegressor
except ImportError:
    XGBRegressor = None
try:
    from lightgbm import LGBMRegressor
except ImportError:
    LGBMRegressor = None

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
APP_DATA = ROOT / "app_data"   # gzipped copies committed for hosting (data/ itself is gitignored)


def data_path(name):
    p = PROCESSED / name
    return p if p.exists() else APP_DATA / f"{name}.gz"

# One target per theme. `leak` = indicators that are near-definitional for the target and would
# make the task trivial (e.g. infant mortality is a component of life expectancy).
THEMES = {
    "Economy":     dict(target="gdp_pc", log=True, leak=["gdp_pc_ppp", "gdp_growth"]),
    "Demography":  dict(target="fertility", log=False, leak=["age0_14", "age65", "pop_growth"]),
    "Health":      dict(target="life_exp", log=False, leak=["infant_mort", "u5_mort"]),
    "Education":   dict(target="enrol_secondary", log=False, leak=["enrol_primary", "enrol_tertiary"]),
    "Environment": dict(target="co2_pc", log=True, leak=["energy_pc"]),
    "Technology":  dict(target="internet", log=False, leak=["mobile"]),
}
NON_FEATURES = {"CountryCode", "Year", "ShortName", "Region", "Income", "population"}
LOG_FEATURES = ["gdp_pc", "gdp_pc_ppp", "co2_pc", "energy_pc", "inflation", "trade_open"]


def _scaled_y(model):
    # SVR and MLP are sensitive to the target's scale (years vs log-dollars), so standardise y too.
    return TransformedTargetRegressor(model, transformer=StandardScaler())


def _models(seed):
    """Model zoo. Every factory takes the seed so runs are reproducible and seed-variance is measurable."""
    m = {
        "Linear":            LinearRegression(),
        "Ridge":             Ridge(alpha=1.0),
        "Lasso":             Lasso(alpha=0.01, max_iter=20000),
        "ElasticNet":        ElasticNet(alpha=0.01, l1_ratio=0.5, max_iter=20000),
        "BayesianRidge":     BayesianRidge(),
        "Huber":             HuberRegressor(max_iter=2000),
        "KNN":               KNeighborsRegressor(n_neighbors=7, weights="distance"),
        "SVR":               _scaled_y(SVR(C=3, epsilon=0.05)),
        "DecisionTree":      DecisionTreeRegressor(min_samples_leaf=5, random_state=seed),
        "RandomForest":      RandomForestRegressor(300, min_samples_leaf=2, n_jobs=-1, random_state=seed),
        "ExtraTrees":        ExtraTreesRegressor(400, min_samples_leaf=2, n_jobs=-1, random_state=seed),
        "GradientBoosting":  GradientBoostingRegressor(n_estimators=300, max_depth=3, learning_rate=0.05,
                                                       subsample=0.8, random_state=seed),
        "HistGB":            HistGradientBoostingRegressor(max_iter=400, learning_rate=0.05, random_state=seed),
        "AdaBoost":          AdaBoostRegressor(DecisionTreeRegressor(max_depth=4), n_estimators=200,
                                               learning_rate=0.05, random_state=seed),
        "MLP":               _scaled_y(MLPRegressor(hidden_layer_sizes=(64, 32), alpha=1e-2, max_iter=3000,
                                                    early_stopping=True, n_iter_no_change=30, random_state=seed)),
    }
    if XGBRegressor is not None:
        m["XGBoost"] = XGBRegressor(n_estimators=500, max_depth=4, learning_rate=0.05, subsample=0.8,
                                    colsample_bytree=0.8, n_jobs=-1, random_state=seed, verbosity=0)
    if LGBMRegressor is not None:
        m["LightGBM"] = LGBMRegressor(n_estimators=500, learning_rate=0.05, num_leaves=31, subsample=0.8,
                                      subsample_freq=1, colsample_bytree=0.8, random_state=seed, verbose=-1)
    base = [(k, m[k]) for k in ("Ridge", "SVR", "RandomForest", "ExtraTrees", "HistGB")]
    m["Voting"] = VotingRegressor(base, n_jobs=-1)
    m["Stacking"] = StackingRegressor(base, final_estimator=Ridge(), cv=3, n_jobs=-1)
    return m


MODEL_NAMES = list(_models(0))
DEFAULT_MODELS = MODEL_NAMES


def _imputer(kind, seed):
    return {"median": SimpleImputer(strategy="median"),
            "knn": KNNImputer(n_neighbors=5),
            "iterative": IterativeImputer(max_iter=10, random_state=seed)}[kind]


@dataclass
class Config:
    themes: list = field(default_factory=lambda: list(THEMES))
    models: list = field(default_factory=lambda: list(DEFAULT_MODELS))
    seeds: list = field(default_factory=lambda: [0, 1, 2])
    folds: int = 5
    mode: str = "panel"          # "panel" = country-years 1990-2014, "snapshot" = latest value per country
    impute: str = "median"       # median | knn | iterative
    min_coverage: float = 0.5    # drop features observed in fewer rows than this
    include_year: bool = True    # panel mode only: lets models learn the global time trend
    years: tuple = (1990, 2014)
    feature_set: str = "all"     # "all" | "income_only" (log GDP per capita alone; used by wdi/story/part2.py)


def load(mode="panel", years=(1990, 2014)):
    if mode == "panel":
        df = pd.read_csv(data_path("wdi_panel_wide.csv"))
        return df[df.Year.between(*years)].reset_index(drop=True)
    df = pd.read_csv(data_path("wdi_snapshot_2005_2014.csv")).rename(columns={"Unnamed: 0": "CountryCode"})
    return df.assign(Year=np.nan)


def dataset(df, theme, cfg):
    """Return X, y, groups (country), and the row metadata for one theme."""
    spec = THEMES[theme]
    keep = df[spec["target"]].notna()
    if cfg.feature_set == "income_only":   # a single predictor: never impute it
        keep &= df["gdp_pc"].notna()
    d = df[keep].reset_index(drop=True)
    y = np.log10(d[spec["target"]].clip(lower=1e-3)) if spec["log"] else d[spec["target"]]
    drop = NON_FEATURES | {spec["target"]} | set(spec["leak"])
    feats = [c for c in d.columns if c not in drop and pd.api.types.is_numeric_dtype(d[c])
             and d[c].notna().mean() >= cfg.min_coverage]
    if cfg.feature_set == "income_only":
        if spec["target"] == "gdp_pc":
            raise ValueError("income_only is undefined when the target is income itself")
        feats = ["gdp_pc"]
    X = d[feats].copy()
    for c in set(LOG_FEATURES) & set(feats):
        X[c] = np.sign(X[c]) * np.log10(1 + X[c].abs())
    if cfg.mode == "panel" and cfg.include_year and cfg.feature_set == "all":
        X["Year"] = d["Year"]
    meta = d[["CountryCode", "Year", "ShortName", "Region", "Income"]]
    return X, y.to_numpy(), d["CountryCode"].to_numpy(), meta


def pipeline(model, cfg, seed):
    return make_pipeline(_imputer(cfg.impute, seed), StandardScaler(), model)


def evaluate(cfg, progress=None):
    """Run every theme x model x seed with grouped K-fold CV.

    Returns (metrics, oof): metrics has one row per theme/model/seed; oof holds out-of-fold
    predictions (target scale, back-transformed for log targets) for the trend view.
    """
    df = load(cfg.mode, cfg.years)
    rows, oof = [], []
    jobs = [(t, m, s) for t in cfg.themes for m in cfg.models for s in cfg.seeds]
    for i, (theme, name, seed) in enumerate(jobs):
        X, y, groups, meta = dataset(df, theme, cfg)
        cv = GroupKFold(cfg.folds, shuffle=True, random_state=seed)
        pred = np.empty_like(y, dtype=float)
        est = pipeline(_models(seed)[name], cfg, seed)
        for tr, te in cv.split(X, y, groups):
            pred[te] = clone(est).fit(X.iloc[tr], y[tr]).predict(X.iloc[te])
        rows.append({"theme": theme, "target": THEMES[theme]["target"], "model": name, "seed": seed,
                     "n": len(y), "n_features": X.shape[1], "r2": r2_score(y, pred),
                     "mae": mean_absolute_error(y, pred), "rmse": mean_squared_error(y, pred) ** 0.5})
        back = (lambda v: 10 ** v) if THEMES[theme]["log"] else (lambda v: v)
        oof.append(meta.assign(theme=theme, model=name, seed=seed, actual=back(y), pred=back(pred)))
        if progress:
            progress(i + 1, len(jobs), rows[-1])
    return pd.DataFrame(rows), pd.concat(oof, ignore_index=True)


def summarise(metrics):
    """Mean ± std across seeds, ranked by R² inside each theme."""
    s = (metrics.groupby(["theme", "model"])[["r2", "mae", "rmse"]].agg(["mean", "std"]))
    s.columns = [f"{a}_{b}" for a, b in s.columns]
    return s.reset_index().sort_values(["theme", "r2_mean"], ascending=[True, False])


def trends(oof, by="Income"):
    """Actual vs model-mean prediction per group and year (panel mode).

    Predictions are first averaged across models and seeds per country-year (an ensemble of the
    whole zoo), then the median across countries is taken per group, matching the notebook trends.
    """
    keys = ["theme", "CountryCode", "Year", by]
    per_row = oof.groupby(keys, observed=True).agg(actual=("actual", "first"), pred=("pred", "mean"),
                                                   pred_std=("pred", "std")).reset_index()
    return per_row.groupby(["theme", by, "Year"], observed=True)[["actual", "pred", "pred_std"]].median().reset_index()


def importance(theme, model="RandomForest", cfg=None, seed=0, repeats=5):
    """Permutation importance on a held-out 25% of countries (drop in R² when a feature is shuffled)."""
    cfg = cfg or Config()
    X, y, groups, _ = dataset(load(cfg.mode, cfg.years), theme, cfg)
    tr, te = next(GroupShuffleSplit(1, test_size=0.25, random_state=seed).split(X, y, groups))
    est = pipeline(_models(seed)[model], cfg, seed).fit(X.iloc[tr], y[tr])
    pi = permutation_importance(est, X.iloc[te], y[te], n_repeats=repeats, random_state=seed, n_jobs=-1)
    return (pd.DataFrame({"feature": X.columns, "importance": pi.importances_mean, "std": pi.importances_std})
            .sort_values("importance", ascending=False).reset_index(drop=True))

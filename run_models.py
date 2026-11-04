"""CLI: evaluate the model zoo on every theme and write results/ for the notebook and the app.

Examples
  python run_models.py                                   # all themes, all models, seeds 0 1 2, panel mode
  python run_models.py --mode snapshot --seeds 0 1 2 3 4
  python run_models.py --themes Health --models Ridge RandomForest XGBoost --impute knn --folds 10
"""
import argparse
import time
from pathlib import Path

from wdi.models import MODEL_NAMES, THEMES, Config, evaluate, importance, summarise, trends

p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
p.add_argument("--themes", nargs="+", default=list(THEMES), choices=list(THEMES))
p.add_argument("--models", nargs="+", default=MODEL_NAMES, choices=MODEL_NAMES)
p.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2])
p.add_argument("--folds", type=int, default=5)
p.add_argument("--mode", choices=["panel", "snapshot"], default="panel")
p.add_argument("--impute", choices=["median", "knn", "iterative"], default="median")
p.add_argument("--min-coverage", type=float, default=0.5)
p.add_argument("--no-year", action="store_true", help="panel mode: do not use Year as a feature")
p.add_argument("--out", default="results")
a = p.parse_args()

cfg = Config(themes=a.themes, models=a.models, seeds=a.seeds, folds=a.folds, mode=a.mode,
             impute=a.impute, min_coverage=a.min_coverage, include_year=not a.no_year)
out = Path(a.out)
out.mkdir(exist_ok=True)
t0 = time.time()


def progress(i, n, r):
    print(f"[{i:>4}/{n}] {time.time() - t0:6.0f}s  {r['theme']:<11} {r['model']:<17} seed={r['seed']}  "
          f"R2={r['r2']:.3f}", flush=True)


metrics, oof = evaluate(cfg, progress)
summary = summarise(metrics)
tag = a.mode
metrics.to_csv(out / f"metrics_{tag}.csv", index=False)
summary.to_csv(out / f"summary_{tag}.csv", index=False)
if a.mode == "panel":
    trends(oof, "Income").to_csv(out / "trends_income.csv", index=False)
    trends(oof, "Region").to_csv(out / "trends_region.csv", index=False)

# Permutation importance for each theme's best model (seed 0).
imps = []
for theme in a.themes:
    best = summary[summary.theme == theme].iloc[0]["model"]
    imps.append(importance(theme, best, cfg).assign(theme=theme, model=best))
import pandas as pd  # noqa: E402
pd.concat(imps).to_csv(out / f"importance_{tag}.csv", index=False)

print(f"\nDone in {time.time() - t0:.0f}s. Best model per theme (mean ± std R² over seeds {a.seeds}):")
for theme, g in summary.groupby("theme"):
    b = g.iloc[0]
    print(f"  {theme:<11} {b.model:<17} R2 {b.r2_mean:.3f} ± {b.r2_std:.3f}   MAE {b.mae_mean:.3f}")

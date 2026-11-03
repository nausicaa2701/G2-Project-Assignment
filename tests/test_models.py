"""Smoke check for wdi.models: run with `python tests/test_models.py` (needs data/processed from the notebook)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from wdi.models import THEMES, Config, dataset, evaluate, load, summarise  # noqa: E402

cfg = Config(themes=["Health"], models=["Ridge", "RandomForest"], seeds=[0, 1], folds=3)

# No target or leaky indicator may leak into the features of any theme.
df = load(cfg.mode)
for theme, spec in THEMES.items():
    X, y, groups, _ = dataset(df, theme, cfg)
    assert spec["target"] not in X and not set(spec["leak"]) & set(X), theme
    assert len(X) == len(y) == len(groups)

metrics, oof = evaluate(cfg)
assert len(metrics) == 4 and len(oof) == 4 * metrics.n.iloc[0]
assert metrics.r2.min() > 0.6, metrics            # life expectancy is very predictable from the rest
s = summarise(metrics)
assert s.r2_std.notna().all()                      # two seeds -> a std per model
print("ok", s[["model", "r2_mean", "r2_std"]].to_string(index=False))

"""Smoke check for Part 2 (WHY): run with `python tests/test_part2.py`. Uses app_data/, about 20 s."""
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from wdi.models import Config, dataset, load  # noqa: E402
from wdi.story import part2  # noqa: E402

# income_only really is a single predictor, never imputed, and is refused for the income target itself.
cfg = Config(mode="snapshot", feature_set="income_only")
df = load("snapshot")
X, y, groups, _ = dataset(df, "Health", cfg)
assert list(X.columns) == ["gdp_pc"] and X.gdp_pc.notna().all()
try:
    dataset(df, "Economy", cfg)
    raise AssertionError("income_only must be refused for the Economy theme")
except ValueError:
    pass

# E2.1: layers are ordered and income alone already explains a large share.
layers = part2.layer_table(part2.r2_layers(seeds=[0, 1], folds=5))
assert (layers.income <= layers.best + 1e-9).all(), layers
assert layers.income_share.mean() > 0.6, layers

# E2.2: Vietnam is the top over-performer on life expectancy (REPORT: +10.4 years).
res = part2.residuals(seeds=[0, 1], folds=5)
vn = res[(res.CountryCode == "VNM") & (res.theme == "Health")].iloc[0]
assert 9 < vn.gap < 12 and vn["rank"] <= 3, vn
assert res.groupby("theme").score.agg(["min", "max"]).pipe(lambda m: (m["min"] > 0) & (m["max"] <= 100)).all()

# Preston slope matches the notebook (~10 years per 10x income, R² ~0.65).
fit = part2.income_fit().set_index("theme").loc["Health"]
assert 9 < fit.slope_per_10x < 11 and 0.6 < fit.r2 < 0.7, fit

# E2.3: within-country slope is positive but much smaller than the cross-country one.
fe, yfx = part2.fixed_effects()
h = fe.set_index("theme").loc["Health"]
assert 0 < h.within < h["between"] / 2, h
assert yfx[yfx.theme == "Health"].effect.iloc[-1] > 3

# run() writes all five result files.
with tempfile.TemporaryDirectory() as tmp:
    part2.run(seeds=[0, 1], folds=5, out=tmp, log=lambda m: None)
    assert len(list(Path(tmp).glob("E2_*.csv"))) == 5

# The app (incl. the story helpers and the Part 2 imports) loads without exceptions.
try:
    from streamlit.testing.v1 import AppTest
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=120).run()
    assert not at.exception, at.exception
except ImportError:
    print("streamlit not installed: app load check skipped")

print("ok", layers[["theme", "income", "all", "best"]].round(2).to_string(index=False))

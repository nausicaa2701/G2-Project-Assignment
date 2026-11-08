"""Smoke check for wdi.story: run with `python tests/test_story.py`."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from wdi import story  # noqa: E402

# Within transformation removes country and year means: a pure FE panel demeans to ~0.
c, t = np.repeat(np.arange(4), 5), np.tile(np.arange(5), 4)
assert np.abs(story._demean2(c * 3.0 + t * 0.5, c, t)).max() < 1e-8
# Weighted CV reduces to the plain CV with equal weights.
x = np.array([1.0, 2, 3, 4])
assert abs(story.wcv(x) - x.std() / x.mean()) < 1e-12

sig = story.e1_1_sigma(vars_=["life_exp"])
assert sig.cv.iloc[-1] < sig.cv.iloc[0]                       # health converges (E1.1)
fe, _ = story.e2_3_fixed_effects()
assert fe.slope_per_10x.iloc[2] < fe.slope_per_10x.iloc[0]    # within-country slope < between (E2.3)
d, X, Z = story.cluster_matrix(story.snapshot())
lab = story.fit_clusters(Z, X.gdp_pc)
assert sorted(set(lab)) == [1, 2, 3, 4] and round(story.income_agreement(lab, d.Income), 2) == 0.74   # report: 74 %
tw = story.e3_2_twins()
assert story.VN not in set(tw.CountryCode) and len(tw) == 10

# A · exploration and B · preprocessing checks (wdi/story/explore.py) reproduce the report's numbers.
snap = story.snapshot()
v = story.validation().set_index("check").found
assert v["duplicate (country, year) keys"] == 0 and v["hyperinflation years (> 500 %)"] == 29
sz = story.sample_sizes(snap).set_index("sample").countries
assert sz["listwise: all 32 indicators"] == 69 and sz["listwise: 15 clustering indicators"] == 147
var, load = story.pca_variance(snap)
assert abs(var["explained_%"].iloc[0] - 63.5) < 0.5 and load.set_index("indicator").PC1["gdp_pc"] > 0
sk = story.skew_transform(snap).set_index("indicator")
assert (sk.skew_log10.abs() < sk.skew_raw.abs()).all()                # log10 reduces skew everywhere
cov = story.coverage_table(snap)
assert len(cov) == 32 and cov.loc[~cov["exploration (≥ 60 %)"], "indicator"].tolist() == ["poverty_190"]
assert story.coverage_by_decade().shape == (32, 6)
print("ok")

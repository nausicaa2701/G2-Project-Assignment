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
assert sorted(set(lab)) == [1, 2, 3, 4] and story.income_agreement(lab, d.Income) > 0.6
tw = story.e3_2_twins()
assert story.VN not in set(tw.CountryCode) and len(tw) == 10
print("ok")

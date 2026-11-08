"""Experiments behind the notebook (section 10) and the app.

    common.py    shared constants (Vietnam, peers, clustering variables) and data loaders
    explore.py   A · data exploration (A1-A3) and B · preprocessing checks
    part1.py     Part 1 · WHAT     E1.1 sigma-convergence, E1.2 beta-convergence, E1.3 robustness
    part2.py     Part 2 · WHY      E2.1 R² layers, E2.2 residual scorecard, E2.3 fixed effects
    part3.py     Part 3 · SO WHAT  E3.1 cluster robustness, E3.2 development twins, E3.3 Vietnam gaps

Run all:   python -m wdi.story            -> results/story/*.csv, figures/story/*.png
Run some:  python -m wdi.story A1 B E2.1 --seeds 0 1 2 3 4
Every experiment is a function returning a DataFrame; `main` saves it and draws one figure.
Everything is re-exported here, so `from wdi import story; story.e1_1_sigma()` keeps working.
"""
import sys

from wdi.story.common import *  # noqa: F401,F403
from wdi.story.common import OUT
from wdi.story.explore import *  # noqa: F401,F403
from wdi.story.explore import (coverage_by_decade, coverage_table, fig_missing, missing_corr_impact,
                               missing_impact, obs_per_year, outliers, pca_variance, sample_sizes,
                               skew_transform, summary_stats, validation)
from wdi.story.part1 import *  # noqa: F401,F403
from wdi.story.part1 import e1_1_sigma, e1_2_beta, e1_3_robustness, fig_beta, fig_sigma
from wdi.story.part2 import (_demean2, _ols_cluster, e2_1_r2_layers, e2_2_residuals,  # noqa: F401
                             e2_3_fixed_effects, fig_fe, fig_r2, fig_residuals)
from wdi.story.part3 import *  # noqa: F401,F403
from wdi.story.part3 import (e3_1_cluster_robustness, e3_2_twins, e3_3_gaps, fig_clusters,
                             fig_gaps)

ALL = ["A1", "A2", "A3", "B", "E1.1", "E1.2", "E1.3", "E2.1", "E2.2", "E2.3", "E3.1", "E3.2", "E3.3"]


def main(argv):
    seeds = [0, 1, 2, 3, 4]
    if "--seeds" in argv:
        k = argv.index("--seeds")
        seeds = [int(s) for s in argv[k + 1:]]
        argv = argv[:k]
    if argv == ["figs"]:
        return redraw()
    want = set(argv) or set(ALL)
    OUT.mkdir(parents=True, exist_ok=True)

    def save(d, name, index=False):
        d.to_csv(OUT / name, index=index)
        print(f"\n== {name}\n{d.head(30).to_string()}")

    # ---- A · exploration, B · preprocessing
    if "A1" in want:
        save(obs_per_year(), "A1_obs_per_year.csv")
        save(coverage_by_decade().round(1), "A1_coverage_decade.csv", index=True)
    if "A2" in want:
        save(summary_stats().reset_index(names="indicator"), "A2_summary_stats.csv")
        save(missing_impact(), "A2_missing_impact.csv")
        fig_missing()
    if "A3" in want:
        c = missing_corr_impact()
        save(c, "A3_missing_corr.csv")
        print("listwise n:", c.attrs)
        save(outliers(), "A3_outliers.csv")
    if "B" in want:
        save(validation(), "B1_validation.csv")
        save(coverage_table(), "B1_coverage.csv")
        save(sample_sizes(), "B1_sample_sizes.csv")
        save(skew_transform(), "B3_skew.csv")
        var, load = pca_variance()
        save(var, "B4_pca_variance.csv")
        save(load, "B4_pca_loadings.csv")
    # ---- Part 1 · WHAT
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
    # ---- Part 2 · WHY (analysis variant; the app variant is `python run_story.py --part 2`)
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
    # ---- Part 3 · SO WHAT
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


def redraw():
    """Redraw the experiment figures from the saved CSVs (no recomputation): python -m wdi.story figs"""
    import pandas as pd
    r = lambda n: pd.read_csv(OUT / n)
    fig_sigma(r("E1_1_sigma.csv"), None)
    res, pts = e1_2_beta()           # the scatter points are not saved; recomputing them is cheap
    fig_beta(pts, res)
    fig_r2(r("E2_1_r2_layers.csv"))
    fig_residuals(r("E2_2_residuals_all.csv"), r("E2_2_residuals_focus.csv"))
    fig_fe(r("E2_3_fixed_effects.csv"))
    fig_clusters(r("E3_1_cluster_robustness.csv"))
    fig_gaps(r("E3_3_gaps.csv"))


if __name__ == "__main__":
    main(sys.argv[1:])

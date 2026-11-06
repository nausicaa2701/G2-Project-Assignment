# Experiment design for the storyline

The storyline ([storyline.md](storyline.md)) asks one question: **"Does richer mean more developed?"** Each part needs experiments that *prove* its message, not just illustrate it. Each part has 3 experiments, and each experiment produces **one main figure for one slide**.

All nine are implemented in [`wdi/story.py`](../wdi/story.py):

```bash
python -m wdi.story                       # all experiments -> results/story/*.csv, figures/story/*.png
python -m wdi.story E2.1 E2.2 --seeds 0 1 2 3 4
python tests/test_story.py                # smoke check
```

## General principles

1. **Hypothesis first, results second.** Each experiment states the hypothesis, the measurement, the acceptance threshold, and *how the story changes if the result goes the other way*.
2. **Reuse the existing pipeline.** `THEMES`, `data_path`, the leakage lists (`leak`) and country-grouped CV all come from `wdi/models.py`. Results are mean ± std over 5 seeds, as in `run_models.py`.
3. **Every conclusion gets at least one robustness check**: different data, a different method, or different weights.
4. **Speak the audience's language.** Use "years of life expectancy", "times more CO₂", "rank out of 192 countries", not only R².

> **Status:** ✅ done and in the repo. The numbers below are the final runs (Ridge, group-median imputation, 5-fold country-grouped CV, 5 seeds), which replace the earlier single-run pilot.

---

## Part 1 · WHAT: "The world progressed, but unevenly"

### E1.1 σ-convergence: what converges and what does not ✅ → figure for slide 1.1 (hook)
- **Hypothesis:** cross-country dispersion of social indicators falls sharply, while income dispersion does not.
- **Measure:** coefficient of variation (CV = std / mean) across countries for each year, only for years with > 100 reporting countries.
- **Result** (`results/story/E1_1_sigma.csv`, `figures/story/E1_1_sigma.png`):

  | Indicator | First year | Last year | Conclusion |
  |---|---|---|---|
  | Life expectancy | 0.23 (1960) | 0.12 (2013) | halved, converging |
  | Primary enrolment | 0.40 (1971) | 0.13 (2013) | strong convergence |
  | Internet users | 4.49 (1990) | 0.65 (2014) | very strong convergence |
  | GDP per capita | 1.46 (1967) | 1.46 (2014) | **flat** |
  | Fertility | 0.31 (1960) | 0.50 (2013) | **diverging**: Sub-Saharan Africa stalled |
  | Under-5 mortality | 0.64 (1962) | 1.02 (2015) | diverging *in relative terms*: rich countries approach zero, so the ratio grows even though absolute gaps shrink |

- **If the result had been the opposite:** if income had converged too, the opening paradox would not exist and the hook would need to change. It did not.

### E1.2 β-convergence for social indicators too ✅ → slide 1.5
- **Hypothesis:** countries that start lower improve faster in life expectancy and schooling (clearly negative β), while for income β is weak.
- **Measure:** regress the annual change 1990 → latest year on the 1990 level, for 4 indicators. GDP uses log growth (%/yr) on the log₁₀ level.
- **Result** (`E1_2_beta.csv`, `E1_2_beta.png`):

  | Indicator | Period | n | β (95 % CI) | r | p |
  |---|---|---|---|---|---|
  | GDP per capita | 1990–2014 | 157 | −0.44 (−0.89, 0.01) | −0.15 | 0.054 |
  | Life expectancy | 1990–2013 | 195 | −0.010 (−0.013, −0.008) | −0.52 | < 0.001 |
  | Primary enrolment | 1990–2013 | 105 | −0.038 (−0.042, −0.033) | −0.85 | < 0.001 |
  | Fertility | 1990–2013 | 195 | −0.015 (−0.017, −0.013) | −0.70 | < 0.001 |

  Vietnam grew 5.3 %/yr, far above the line for its 1990 income.
- **Conclusion:** social catch-up is strong and significant; income catch-up is weak and not significant at 5 %.

### E1.3 Data robustness: is the convergence an artefact of missing data? ✅ → slide 1.2
- **Concern:** poorer countries report less, so "convergence" could be an illusion caused by the set of countries changing over time.
- **Measure:** CV change 1990 → 2013 for (a) all reporting countries, (b) a **balanced panel** (only countries reporting in both years), (c) the balanced panel **weighted by population**.
- **Accept if:** the direction does not change in (b) and (c).
- **Result** (`E1_3_robustness.csv`): the direction holds for life expectancy (−21 % / −22 % / −20 %), primary enrolment (−44 % / −52 % / −40 %), internet (−85 % in all three) and under-5 mortality (diverging in all three). Fertility is diverging or flat (+6 % / +5 % / +7 %). **GDP is the exception worth stating:** its CV falls 13 % with all reporting countries but only 5 % on the balanced panel, so more than half of the apparent income convergence since 1990 comes from countries entering the data.
- Slide 1.2 sentence: *"The conclusions hold when we keep only countries with complete data, and when we weight by population."*

---

## Part 2 · WHY: "Income explains most of it; the residual is the story"

### E2.1 How much does income explain? R² in three layers ✅ → slide 2.3 (replaces the 19-model slide)
- **Hypothesis:** log GDP per capita alone explains about 2/3 in most themes. Other indicators help moderately; non-linear models help very little.
- **Measure:** for each theme, three configurations with the same folds: ① Ridge on log GDP only → ② Ridge on all features → ③ best model from the 19-model suite (`results/summary_snapshot.csv`). Economy is excluded because its target is income itself.
- **Result** (`E2_1_r2_layers.csv`, `E2_1_r2_layers.png`, mean ± std over 5 seeds):

  | Theme (target) | ① income only | ② all features | ③ best model |
  |---|---|---|---|
  | Technology (internet) | 0.77 ± 0.00 | 0.79 ± 0.01 | 0.85 (ExtraTrees) |
  | Environment (CO₂, log) | 0.68 ± 0.00 | 0.84 ± 0.01 | 0.87 (Voting) |
  | Health (life expectancy) | 0.60 ± 0.00 | 0.79 ± 0.01 | 0.81 (Voting) |
  | Education (secondary enrolment) | 0.58 ± 0.00 | 0.74 ± 0.01 | 0.77 (Stacking) |
  | Demography (fertility) | 0.51 ± 0.01 | 0.77 ± 0.02 | 0.82 (Voting) |
  | *mean* | *0.63* | *0.79* | *0.82* |

- **Conclusion:** income alone carries most of the explained variance (on average 0.63 of 0.82, i.e. about three quarters of what the best model achieves). Other indicators add 0.16, complex models only 0.03 more. The claim "about 2/3" holds roughly in all five themes (0.51–0.77), not just health.

### E2.2 Vietnam's residual scorecard ✅ → slide 2.4 (the most important slide)
- **Hypothesis:** Vietnam does better than its income predicts on social indicators.
- **Measure:** out-of-fold residual of model ① (income only), averaged over 5 seeds, converted to the target's own units (ratio for log targets) and ranked among all countries.
- **Result** (`E2_2_residuals_focus.csv`, full table in `E2_2_residuals_all.csv`):

  | Indicator | Actual vs income-predicted | Rank (1 = most above expectation) |
  |---|---|---|
  | Life expectancy | **+10.4 years** (75.8 vs 65.4) | **1 / 203** |
  | Internet users | +25.0 per 100 (48.3 vs 23.3) | 4 / 204 |
  | Fertility | −1.9 births per woman (1.74 vs 3.69) | 201 / 203 (far lower than expected) |
  | **CO₂ per capita** | **3.2× the predicted level** (1.97 t vs 0.61 t) | 17 / 199 |
  | Secondary enrolment | not reported by Vietnam in 2005–2014 | n/a |

  Peers for comparison: China +4.4 years (rank 30), Thailand +3.4 (47); China emits 3.6×, Thailand 2.4× its predicted CO₂.
- **Finding for Part 3:** Vietnam beats expectations socially, but **emits about 3 times what its income predicts**. The "price of growth" slide (2.5) therefore has a concrete example close to home.

### E2.3 "Being richer" vs "getting richer": the within-country view ✅ → backup for slide 2.2
- **Concern:** the Preston curve is a *between-country* association. The panel may ask: when a country gets richer, does its life expectancy rise by the same amount?
- **Measure:** panel 1990–2014 (4,377 country-years, 196 countries), life expectancy on log₁₀ GDP per capita. Between-country regression on country means, pooled OLS, and two-way fixed effects (country + year) by alternating demeaning in numpy. Standard errors clustered by country.
- **Result** (`E2_3_fixed_effects.csv`, `E2_3_fixed_effects.png`):

  | Model | Years per 10× GDP per capita | 95 % CI |
  |---|---|---|
  | Between countries | 10.9 | 9.8 – 12.0 |
  | Pooled OLS | 11.1 | 10.1 – 12.1 |
  | Two-way fixed effects | **3.2** | 1.3 – 5.2 |

- **Interpretation:** within a country, getting richer goes with a much smaller gain (about 1/3 of the cross-sectional slope). Most of the gain over time is a common shift shared by all countries (medicine, vaccines, knowledge), which explains why the whole curve moved up ~5 years and supports "policy can shift the curve". This also answers the "fixed-effects panel models" next step listed in the old REPORT.

---

## Part 3 · SO WHAT: "Look with data, not only with income"

### E3.1 Are the clusters robust? ✅ → slide 3.2
- **Concern:** the silhouette is low (0.19 at k = 4), so a country's cluster could depend on the seed or the algorithm.
- **Measure:** K-means, Gaussian mixture and Ward with 20 seeds each, on the same 15 standardised indicators as the app. Measure (a) ARI between seeds and vs the reference run (K-means, seed 42, the app default), (b) **share of runs with Vietnam in the "emerging" cluster**, (c) agreement with income groups.
- **Accept if:** Vietnam is "emerging" in ≥ 80 % of runs. Otherwise slide 3.2 says "Vietnam sits on the boundary between two clusters".
- **Result** (`E3_1_cluster_robustness.csv`, `E3_1_runs.csv`, `E3_1_country_stability.csv`):

  | Algorithm | ARI between seeds | ARI vs reference | Agreement with income groups | Vietnam "emerging" |
  |---|---|---|---|---|
  | K-means | 0.93 | 0.95 | 0.74 | **90 %** |
  | Gaussian mixture | 0.70 | 0.54 | 0.63 | 35 % |
  | Ward | 1.00 (deterministic) | 0.55 | 0.65 | 0 % |

- **Conclusion:** K-means is stable, but the partition changes with the algorithm. Vietnam passes the threshold only under K-means, so the honest phrasing is **"Vietnam sits on the boundary between transition and emerging"**.

### E3.2 Vietnam's "development twins" ✅ → slide 3.3
- **Question:** which countries is Vietnam most *similar* to if we ignore income?
- **Measure:** standardise 10 social indicators (life expectancy, under-5 mortality, fertility, age 65+, secondary enrolment, internet, mobile, electricity, safe water, urbanisation), **without** GDP or energy, and take the 5 nearest countries by Euclidean distance. Compare with the 5 nearest by GDP per capita only.
- **Result** (`E3_2_twins.csv`):

  | Same income | Same social outcomes (income in brackets vs Vietnam) |
  |---|---|
  | Côte d'Ivoire | Seychelles (14.5×) |
  | São Tomé and Príncipe | Mauritius (6.6×) |
  | Nigeria | Thailand (3.5×) |
  | Solomon Islands | Grenada (6.2×) |
  | Zambia | St. Lucia (5.2×) |

- The right-hand column is 3.5–14.5 times richer, and its life expectancy is 73–75 years like Vietnam's, against 51–68 years on the left: the most visual way to say "Vietnam outperforms its income".

### E3.3 Gap analysis: Vietnam's next priorities ✅ → slide 3.4
- **Measure:** for each indicator, the difference between Vietnam and the median of the "emerging" (and "advanced") cluster, in standard deviations across countries (log scale where noted), ranked.
- **Result** (`E3_3_gaps.csv`, `E3_3_gaps.png`), vs "emerging":
  - Vietnam is **behind** on urbanisation (33 % vs 66 %, −1.4 SD), GDP per capita (US$1,078 vs 5,306, −1.0 SD) and energy use (−0.6 SD).
  - Vietnam is **ahead or equal** on life expectancy, internet, electricity and water; it is more open to trade (+1.5 SD) and more forested (+0.7 SD).
  - Under-5 mortality is higher (22 vs 15 per 1,000, +0.4 SD); against the "advanced" cluster this gap grows to +1.4 SD (22 vs 4).
- **Change from the draft:** we expected child mortality to be the largest gap; it is moderate against the emerging group and large only against advanced economies. The priorities are therefore income, urbanisation and child mortality, with every suggestion backed by a number.

---

## Experiment → slide map

| Slide | Before (existing figure) | After (experiment figure) |
|---|---|---|
| 1.1 hook | 2 numbers | **E1.1** CV lines: social converges, income flat |
| 1.2 data | coverage heatmap | heatmap + one sentence from **E1.3** |
| 1.5 income does not converge | `14_convergence` | **E1.2** β for 4 indicators |
| 2.3 models | 3-model table | **E2.1** R² in 3 layers |
| 2.4 residuals | `17` zoomed | **E2.2** Vietnam scorecard |
| 2.5 CO₂ | `19_ekc` | `19` + Vietnam at 3.2× (from E2.2) |
| 3.2 clusters | `21_pca_clusters` | `21` + robustness from **E3.1** |
| 3.3 Vietnam | `15_vietnam_peers` | **E3.2** development twins |
| 3.4 gaps | `15` | **E3.3** gap chart |

## Code layout (as built)

```
wdi/story.py              # E1.1–E3.3 + report checks (A2 summary/missing impact, A3 outliers); reuses wdi/models.py
results/story/*.csv       # one or more tables per experiment
figures/story/*.png       # one figure per experiment, Vietnam in #c0392b
tests/test_story.py       # smoke check, same style as tests/test_models.py
```
The app's Clusters page now calls the same `cluster_matrix` / `fit_clusters` helpers, so the report and the app always agree.

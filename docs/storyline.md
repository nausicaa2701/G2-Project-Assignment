# Storyline: one question, three parts, one main character

## The big question (the whole talk answers only this)

> **"Does richer mean more developed?"**

**The answer, stated up front (Pyramid Principle):** *Mostly yes: income alone explains about 60 % of the cross-country differences (cross-validated R² 0.51–0.77 across five themes). But the rest is where the story is. Some countries live much better than their income predicts, and Vietnam is the clearest example.*

**Main character:** Vietnam, always drawn in **red** (`#c0392b`, the colour the notebook already uses) on every chart, so the audience always knows which point to look for.

## Three-part frame: What → Why → So what

The three parts map to three levels of analysis: descriptive, diagnostic and prescriptive. Each part ends with a question that the next part answers.

```
PART 1 · WHAT                  PART 2 · WHY                     PART 3 · SO WHAT
"The world progressed,         "Income explains most of it;     "Look with data, not only with
 but unevenly"                  the residual is the story"       income: where does Vietnam stand?"
Description · comparison       Correlation · regression ·       PCA · clustering · case study
over time                      residuals
        │                              │                                │
        └─► Paradox: health            └─► If income does not tell      └─► Answer the big question
            converges, income              the whole story, is grouping     + implications + limits
            does not. So how much          countries by income still
            does income matter?            right?
```

---

## Part 1 · WHAT: "The world progressed, but unevenly" (5 slides, ~7 min)

| # | Action title | Figure | Anchor number |
|---|---|---|---|
| 1.1 | **The rich–poor life-expectancy gap shrank by a third, while the income gap grew** *(hook + big question)* | `story/E1_1_sigma` | gap 30.1 → 20.8 years · p90/p10 77× → 81× · CV of life expectancy 0.23 → 0.12, of GDP 1.46 → 1.46 |
| 1.2 | **55 years, 214 countries, and we know exactly where data is missing** *(credibility, one slide only)* | `01_coverage_heatmap` + `story/A2_missing_by_income` | 45 % of cells empty, mostly structural; 5 handling rules; trends hold on a balanced panel (E1.3) |
| 1.3 | **Health, education, mobile phones: almost everyone moved forward** | `06_trend_health` (+ 07, 09 small) | South Asia +30 years of life expectancy; ~64 mobile subscriptions per 100 in low-income countries |
| 1.4 | **Except one: Sub-Saharan Africa has not completed the demographic transition** | `10_trend_regions` | fertility −28 % vs −60 to −67 % elsewhere; fertility CV rose 0.31 → 0.50 |
| 1.5 | **Income did not converge; only a few countries broke away (Vietnam among them)** | `story/E1_2_beta` | GDP β r = −0.15 (p = 0.05) vs r = −0.52 to −0.85 for health, schooling, fertility; China 9.2 %/yr, Vietnam 5.3–5.5 %/yr |

**Bridge →** *"Health converged while income did not. So how much does income really matter?"*

## Part 2 · WHY: "Income explains most of it; the residual is the story" (5 slides, ~7 min)

| # | Action title | Figure | Anchor number |
|---|---|---|---|
| 2.1 | **Almost every indicator moves with income** | `16_correlation` | ρ life expectancy 0.85 · ρ CO₂ 0.86 |
| 2.2 | **Ten times richer means about ten more years of life** (Preston curve) | `17_preston_curve` | R² 0.65; the whole curve shifted up ~5 years since 1990 |
| 2.3 | **More complex models barely help, because the relationship is simple** | `story/E2_1_r2_layers` | income only: R² 0.51–0.77 → all indicators: 0.74–0.84 → best of 19 models: 0.77–0.87 |
| 2.4 | **The residual: who lives better than their income allows?** *(the most important slide)* | `story/E2_2_residuals` | Vietnam **+10.4 years, rank 1 of 203**; internet +25 points (4/204); fertility −1.9 (201/203) |
| 2.5 | **The price of growth: CO₂ does not fall as countries get richer** | `19_ekc` + Vietnam's point | turning point ~US$51,000; only 9 of 192 countries above it; Vietnam emits **3.2×** what its income predicts |

Backup for 2.2 (E2.3): *"Being richer is not the same as getting richer."* Between countries, 10× income goes with +10.9 years; within the same country over time (two-way fixed effects) only +3.2 years. Most of the gain over time is a common shift (medicine, vaccines), which is why the whole curve moved up.

**Bridge →** *"Income does not tell the whole story. So is grouping countries by income still right?"*

## Part 3 · SO WHAT: "Look with data, not only with income" (5 slides, ~7 min)

| # | Action title | Figure | Anchor number |
|---|---|---|---|
| 3.1 | **Development is mostly one continuous axis, not separate steps** | `21_pca_clusters` (PC1 axis) | PC1 = 63 % of variance; low silhouette → a continuum |
| 3.2 | **Four data-driven clusters match income groups for 74 % of countries; the mismatches are what matter** | `21_pca_clusters` + `story/E3_1_cluster_robustness` | Equatorial Guinea and Angola fall into the low cluster; K-means is stable (ARI 0.93 between seeds) |
| 3.3 | **Vietnam: lower-middle income, but outcomes of richer countries** | `story/E3_2_twins` (+ `15_vietnam_peers`) | same income: Côte d'Ivoire, Nigeria, Zambia; same social outcomes: Seychelles, Mauritius, Thailand (3.5–14.5× richer) |
| 3.4 | **What separates Vietnam from the "emerging" cluster: income and urbanisation** | `story/E3_3_gaps` | GDP −1.0 SD, urban share 33 % vs 66 % (−1.4 SD); under-5 mortality 22 vs 15 per 1,000 |
| 3.5 | **Answer to the big question + implications + limits** | 3 lines of text | see below |

Note for 3.2–3.4: Vietnam is in the "emerging" cluster in 90 % of K-means runs, but only 35 % of Gaussian-mixture runs and never with Ward. Say *"Vietnam sits on the boundary between transition and emerging"*: it is still an insight, just phrased honestly.

**Slide 3.5, closing content:**
- *Answer:* richer mostly means more developed (~60 % of the differences), but policy can shift the whole curve (+5 years worldwide, +10 years for Vietnam).
- *Implications (phrased as suggestions, because this is correlation, not causation):* judge countries on social outcomes, not only on GDP. For Vietnam, the next priorities are child mortality, urbanisation and a lower-carbon growth path than the countries that went before it (it already emits 3.2× what its income predicts).
- *Limits:* data ends in 2014; poorer countries report less; associations, not causal effects; country medians are not population-weighted.
- *Close:* "What is your question?" → open the app (Compare / Clusters pages) and answer live.

---

## Data-analytics skills applied

| Skill | How it is used |
|---|---|
| **One central question** | Every slide must help answer "richer = more developed?"; slides that do not go to the appendix |
| **Pyramid Principle / conclusion first** | The answer appears on slide 1.1; the three parts are the evidence |
| **SCQA** | Situation (1.3) → Complication (1.5: income does not converge) → Question (bridge) → Answer (Parts 2–3) |
| **Action titles** | Titles are conclusions ("Ten times richer…"), not topics ("Preston curve") |
| **One figure, one message, one number** | Each slide has exactly one anchor number for the audience to remember |
| **Purposeful colour** | Grey for every country, red for Vietnam, one accent colour for the group being discussed |
| **Benchmarking** | Vietnam always sits next to a reference (Preston curve, its cluster, its neighbours), never alone |
| **Residual analysis** | The best insights are where the model is wrong (2.4, 3.2), not in the R² |
| **Method builds trust, it is not a show** | ETL and missing data fit in one slide; 19 models and grouped CV go to the appendix |
| **Honest limits** | Use "associated with", "suggests", never "causes"; limits are on the closing slide, not hidden |

## Moved out of the main story (appendix / backup)

| Content | Reason | Use when |
|---|---|---|
| `03_distributions`, `02_snapshot_coverage` | Technical, does not answer the big question | Asked why we use logs |
| `04`, `05`, `08` single-theme trends | Repeat the point of 1.3–1.4 | Part 1 needs to run longer |
| `11`–`13` rankings | 1.4 already makes the "Sub-Saharan Africa lags" point | Asked about top/bottom 10 |
| 19 models, feature importance, panel vs snapshot | Same conclusion as 2.3 | The panel asks about modelling rigour |
| `20_cluster_k` (choice of k) | Technical detail | Asked why k = 4 |
| E2.3 fixed effects, E1.3 robustness table | Robustness, not message | Asked "is this causal?" or "is this a missing-data artefact?" |

## How to extend without breaking the flow
Any new slide must answer: *"Which level of the big question does this slide help with: What, Why or So what?"* If it can, insert it in that part, with an action title and one anchor number. If it cannot, it goes to the appendix.

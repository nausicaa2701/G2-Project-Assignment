# Task split: 3 people · 3 parts · presented with Streamlit

Each person owns **one part of the story** ([storyline.md](storyline.md)), from preprocessing → experiments ([experiments.md](experiments.md)) → **one Streamlit page** used to present live instead of slides.

> **Status (6 Nov 2026):** all nine experiments (E1.1–E3.3) are implemented in `wdi/story.py`, with results in `results/story/` and figures in `figures/story/`, and the final report is written (`report/FINAL_REPORT.pdf`). What remains are the three story pages in the app (A3, B3, C4), deployment (A4) and the integration phase.

| | **Person A · Part 1 WHAT** | **Person B · Part 2 WHY** | **Person C · Part 3 SO WHAT** |
|---|---|---|---|
| Message | The world progressed, but unevenly | Income explains most of it; the residual is the story | Look with data, not only with income |
| Shared infrastructure owned | **Setup + ETL pipeline + deploy** | **Model preprocessing + re-running results** | **Navigation + small helpers + `app.py` review** |
| Own preprocessing | Cleaning, missing data, reshape, balanced panel | Log transform, leakage removal, coverage filter, imputation, country-grouped folds | Choose 15 indicators, standardise, PCA, distance space without GDP |
| Experiments | E1.1 σ-convergence · E1.2 β-convergence · E1.3 data robustness | E2.1 3-layer R² · E2.2 Vietnam residual scorecard · E2.3 fixed effects | E3.1 cluster robustness · E3.2 development twins · E3.3 Vietnam gaps |
| Streamlit page | `page_part1`, reusing Overview + Trends | `page_part2`, reusing Compare (scatter) + Models | `page_part3`, reusing Clusters |

Each person has a similar workload: **1 infrastructure piece + 1 preprocessing piece + 3 experiments + 1 app page (~7 min)**.

---

## Reuse the existing app (do not rebuild)

`app.py` already has a design system (light/dark, `style`, `hero`, `section`, `tiles`, `table`, `LABELS`, `load_data`, `group_trend`) and 5 pages. Most of the story content **already exists**; each person reuses it and *adds* the new experiments.

| Part | Already in `app.py` (reuse) | To add |
|---|---|---|
| **A · WHAT** | `page_overview` (life expectancy by income group, 4 insights), `page_trends` (trends by theme/region, country comparison), `group_trend()` | Coverage heatmap, E1.1 CV lines, E1.2 β, bridge sentence |
| **B · WHY** | `page_compare` → "Relationship explorer" (scatter of any two indicators, for Preston/EKC), `page_models` (R² of 19 models, importance, live experiment) | E2.1 3-layer R², E2.2 Vietnam residual scorecard, Vietnam in red |
| **C · SO WHAT** | `page_clusters` (K-means/GMM/Ward, PCA, map, cluster profiles, % match with income groups) | E3.1 robustness, E3.2 twins, E3.3 gaps, conclusion |

**How:** each person writes **one new page function** `page_part1()` / `page_part2()` / `page_part3()` that calls the existing helpers and chart code, reads `results/story/`, and adds one `st.Page(...)` line to `st.navigation`. The old pages stay as the "Explore" section for Q&A.

```
app.py                    shared  # each person only adds their page_partN function + 1 nav line
wdi/story.py              done    # E1.1–E3.3 (one function per experiment, each returns a DataFrame)
wdi/models.py             B       # exists; only add, do not change existing behaviour
wdi/etl.py                A       # turn notebook cells 4–18 into a runnable script
results/story/E*.csv      done
figures/story/E*.png      done
tests/test_story.py       done
SETUP.md                  A
```

**Conflict rule:** in `app.py`, each person only adds their function in their own region, marked `# ---- part N (owner X)`, and does not edit shared helpers or old pages. Git then merges automatically because changes are in different places. Changes to shared helpers or `requirements.txt` go in a separate PR reviewed by C. Each person works on their own branch: `part1/...`, `part2/...`, `part3/...`.
*Optional, only if `app.py` gets too long:* move the helpers to `ui/common.py`. Not required for the presentation.

---

## Phase 0 · Setup (everyone, blocks later steps)

| ID | Task | Who | Done when |
|---|---|---|---|
| S0.1 | Clone the repo, create a venv, `pip install -r requirements.txt` | A, B, C | `streamlit run app.py` works on everyone's machine |
| S0.2 | Kaggle token, download raw data into `data/raw/` | A, B, C | `Country.csv`, `Series.csv`, `Indicators.csv` present (`database.sqlite` can be deleted) |
| S0.3 | Write `SETUP.md`: commands for macOS/Linux and Windows, common errors | **A** | Someone else can follow it on a clean machine without asking |
| S0.4 | **Add the 3 pages to the nav:** `st.navigation` with two groups, "Story" (`page_part1..3`, empty for now) and "Explore" (the 5 old pages unchanged) | **C** | The app runs as before, with 3 extra entries under Story. About 15 lines |
| S0.5 | **Data contract:** list column names, units and dtypes of `panel`/`snapshot` as a `SCHEMA` constant in `wdi/etl.py` | **A** | B and C import `SCHEMA` instead of guessing column names |
| S0.6 | **Add small helpers** to the existing design system: `VN_COLOR`, `takeaway()`, `bridge()`, `method_box()` (can build on `hero`/`section`/the `.insight` CSS) | **C** | A and B can call them in their page functions |

> S0.4–S0.6 are only a few dozen lines; merge them into `main` on day one, then branch for each part.

---

## Person A · Part 1 WHAT: setup, ETL, "How the world changed"

### A1. Preprocessing pipeline (`wdi/etl.py`)
| ID | Task | Source | Done when |
|---|---|---|---|
| A1.1 | Extract: read `Indicators.csv` in chunks, filter 32 indicators | Notebook cells 6–7 | `python -m wdi.etl` gives the same 247k rows |
| A1.2 | Transform: separate 214 countries from 33 aggregates; merge the High income groups; check duplicates, non-finite values, domain ranges; flag hyperinflation | Cells 10–12 | Log prints rows removed and the 29 flagged years |
| A1.3 | Reshape: long → wide; interpolate gaps ≤ 3 years, no extrapolation; 2005–2014 snapshot | Cells 17–18 | Output **matches** the current `app_data/*.csv.gz` (write a comparison test) |
| A1.4 | Also export `coverage.csv` (indicator × decade) and a `balanced_panel` (countries with complete data) | Cell 15 + new | The Part 1 page can read both |
| A1.5 | Write to `data/processed/` and `app_data/*.gz` | | Notebook and app share the same outputs |

### A2. Experiments — ✅ done in `wdi/story.py`
| ID | Task | Result |
|---|---|---|
| A2.1 | **E1.1** `e1_1_sigma(vars_, min_n=100)` → CV per year | Life expectancy 0.23 → 0.12; GDP 1.46 → 1.46 |
| A2.2 | **E1.2** `e1_2_beta(start=1990, end=2014)` → β, 95 % CI, R² for 4 indicators | GDP r = −0.15, p = 0.054 (notebook: −0.16, 0.05) |
| A2.3 | **E1.3** `e1_3_robustness()`: E1.1 on a balanced panel and population-weighted | Table of "direction holds / changes"; directions hold, GDP convergence is mostly composition |

### A3. Streamlit page `page_part1()` (reuses `page_overview`, `page_trends`, `group_trend`)
1. **Hero:** the big question + the paradox (life-expectancy gap 30 → 21 years while income gap 77× → 81×)
2. **Can we trust the data?** Coverage heatmap + the 5 missing-data rules + E1.3 result (inside `method_box`, opened on demand)
3. **What converges:** E1.1 CV lines, with an indicator selector
4. **The Sub-Saharan exception:** fertility trend by region
5. **Income does not converge:** the 4 β panels from E1.2, Vietnam in red
6. `bridge("Health converged while income did not. So how much does income matter?")`

### A4. Deploy
Push the app to Streamlit Community Cloud and check that it runs with only `app_data/` + `results/`. Also record a screen video as a backup in case there is no network.

---

## Person B · Part 2 WHY: models, "The role of income"

### B1. Model preprocessing (extend `wdi/models.py` without breaking existing code)
| ID | Task | Done when |
|---|---|---|
| B1.1 | Document the existing `dataset()`: log transform (`LOG_FEATURES`), leakage removal (`leak`), coverage filter < 60 %, imputation | Docstring + a table in the page's `method_box` |
| B1.2 | Add `feature_set="income_only" \| "all"` to `Config` | Existing `tests/test_models.py` still passes (E2.1 currently does this inside `wdi/story.py`) |
| B1.3 | `oof_predictions(theme, cfg)` returning out-of-fold predictions and residuals per country, averaged over 5 seeds | ✅ covered by `e2_2_residuals()`: Vietnam's life-expectancy residual +10.4 years |
| B1.4 | Re-run `run_models.py` (snapshot, 5 seeds) to confirm the current `results/` | Differences ≤ 0.01 R² |

### B2. Experiments — ✅ done in `wdi/story.py`
| ID | Task | Result |
|---|---|---|
| B2.1 | **E2.1** 3-layer R² × 5 themes (income only / all features / best model) | `results/story/E2_1_r2_layers.csv`, mean ± std; income only 0.51–0.77 |
| B2.2 | **E2.2** residual scorecard: original units + percentile + rank, for Vietnam and 5 peers | Life expectancy rank 1/203, CO₂ 3.2× |
| B2.3 | **E2.3** two-way fixed effects (country and year demeaning in numpy, **no new library**) | Within-country 3.2 vs between-country 10.9 years per 10× income, with CIs |
| B2.4 | One CLI for all experiments | ✅ `python -m wdi.story [E1.1 …] [--seeds …]` |

### B3. Streamlit page `page_part2()` (reuses the `page_compare` scatter and the `page_models` R² chart)
1. **Hero:** "Ten times richer means ~10 more years of life, but that is not everything"
2. **Everything moves with income:** correlation heatmap, with a toggle to sort indicators by ρ with GDP
3. **Preston curve:** interactive scatter, with a country picker to highlight (default Vietnam)
4. **3-layer R² (E2.1):** stacked bars; `method_box` describes grouped CV, 5 seeds, the 19 models
5. **Vietnam residual scorecard (E2.2):** dot plot, with a country picker so the audience can ask "what about country X?"
6. **The CO₂ price:** Kuznets curve + Vietnam at 3.2×; E2.3 in an expander "Richer vs getting richer"
7. `bridge("Income does not tell the whole story. So is grouping by income still right?")`

---

## Person C · Part 3 SO WHAT: app frame, clustering, "Where Vietnam stands"

### C1. App infrastructure (light, since the app already exists)
S0.4 and S0.6 above, plus:
- `VN_COLOR = "#c0392b"` and `highlight(fig, codes)` so Vietnam is red on every page
- `takeaway(text)`: a conclusion-style heading box; `bridge(text)`: the bridge sentence at the end of a page; `method_box(md)`: a "Method & preprocessing" expander
- A **"Presentation" mode** toggle: hide the sidebar and secondary widgets, larger text, for presenting on stage

### C2. Preprocessing for clustering — ✅ done in `wdi/story.py`
| ID | Task | Result |
|---|---|---|
| C2.1 | Move the preprocessing inside `page_clusters` into `cluster_matrix(snap, vars, log_vars, min_cov=.7)`: log, income-group median imputation, standardisation | ✅ the Clusters page now calls it and shows the same 74 % |
| C2.2 | `fit_clusters(Z, gdp, algo, k, seed)` + order clusters by GDP | ✅ 74 % match at k = 4, K-means |
| C2.3 | Social space: social indicators **without GDP**, standardised (for E3.2) | ✅ `SOCIAL_VARS` in `e3_2_twins()` |

### C3. Experiments — ✅ done in `wdi/story.py`
| ID | Task | Result |
|---|---|---|
| C3.1 | **E3.1** 3 algorithms × 20 seeds: ARI, % runs with Vietnam "emerging", % match with income groups | `results/story/E3_1_cluster_robustness.csv`; K-means robust, Vietnam on the boundary across algorithms |
| C3.2 | **E3.2** 5 nearest countries by GDP vs 5 nearest by social indicators | Côte d'Ivoire, Nigeria… vs Seychelles, Mauritius, Thailand… |
| C3.3 | **E3.3** Vietnam's distance to the "emerging"/"advanced" medians in SD, ranked | Largest gaps: urbanisation and income; child mortality large only vs advanced |

### C4. Streamlit page `page_part3()` (reuses the whole `page_clusters` pipeline)
1. **Hero:** "Look with data, not only with income"
2. **One development axis:** PCA, PC1 = 63 %
3. **Clusters vs income groups:** map + mismatch matrix (74 %) + robustness from E3.1
4. **Vietnam's twins (E3.2):** two columns of country names + a radar chart
5. **The gaps (E3.3):** horizontal bar chart, with a picker for the comparison group (emerging/advanced)
6. **Conclusion:** answer the big question, implications (as suggestions), limits
7. **"What is your question?"**: lead into the Explore section for live demos in Q&A

---

## Final phase · Integration (whole team)

| ID | Task | Who |
|---|---|---|
| I.1 | **Cross-check numbers:** every number on the 3 pages matches `results/` and the report | A checks B's page, B checks C's, C checks A's |
| I.2 | Update REPORT.md/README for the new story | Each person writes their own section |
| I.3 | Rehearse: each page ≤ 7 minutes, transitions via the `bridge` sentences | Whole team |
| I.4 | Backup plan: video + screenshot of each page in `docs/screenshots/` | A |
| I.5 | Q&A prep: each person prepares 3 hard questions on their part, with a `method_box` to open when answering | Each person |

## Order & dependencies

```
Phase 0 (S0.1–S0.6) ─┬─► A1 ETL ──► A2 ✅ ──► A3 ─┐
                     ├─► B1 ──────► B2 ✅ ──► B3 ─┼─► Integration (I.1–I.5) ──► A4 Deploy
                     └─► C2 ✅ ───► C3 ✅ ──► C4 ─┘
```
- After Phase 0, B and C **do not wait** for A1, because they use the existing `app_data/`. A1.3 only has to make sure the new files match the old ones.
- Priority if time is short: the three app pages first (the experiments are done), then A1 ETL script, then the optional helpers.

## Definition of "done" for each page
- [ ] Each section opens with a `takeaway` that is **one conclusion sentence** with one anchor number
- [ ] Vietnam in `VN_COLOR` on every chart
- [ ] Preprocessing and method sit in `method_box`, not on the main screen
- [ ] The page loads in < 3 seconds (reads `results/story/`, no training while presenting)
- [ ] Works in both light and dark mode, and on a projector
- [ ] `tests/test_story.py` passes
- [ ] The page ends with a `bridge` (page 3 ends with the conclusion)

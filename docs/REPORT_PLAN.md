# Final report plan (for review)

**Output:** `FINAL_REPORT.md` in the repo, compiled to `FINAL_REPORT.pdf` (Markdown → HTML → PDF with the Chrome already installed, so nothing new to install). LaTeX is possible but needs MiKTeX/TeX installed first; say if you prefer that.
**Length:** about 15–20 pages with figures. Existing `REPORT.md` stays as the short summary.

## 0. Introduction
Dataset source (World Bank WDI via Kaggle), project goal, the six themes, and the tools used (Python, pandas, scikit-learn, Streamlit).

## A. Initial data exploration
**A1. Dataset overview.** Raw files and sizes (`Indicators.csv` 574 MB, 5.66 M rows; `Country.csv`, `Series.csv`). Attributes table: name, type, meaning (CountryCode, IndicatorCode, Year, Value, Region, IncomeGroup, ...). 247 economies (214 countries + 33 aggregates), 1,344 indicators, 1960–2015. The 32 indicators we selected, grouped by theme. *Summary box.*

**A2. Summary statistics.** Table of count, missing %, mean, median, std, min, max, skewness for the 32 indicators (snapshot). Distribution plots (`03_distributions.png`) and coverage heatmaps (`01`, `02`). **Missing-value impact (new):** for key indicators, compare mean/median computed on (a) reporting countries only, (b) after group-median imputation, plus coverage by income group, showing that poorer countries report less so raw averages are biased upward. *Summary box.*

**A3. Exploration: outliers, clusters, interesting attributes.** Outliers via IQR/z-score (hyperinflation years, Gulf CO₂, Equatorial Guinea income vs health). Correlation structure (`16`), Preston curve (`17`), first look at country groupings (`21`). Interesting attributes and values: life expectancy, fertility in Sub-Saharan Africa, CO₂ per capita, Vietnam as over-performer. **Missing-value impact (new):** how many countries drop out of the correlation/scatter analyses when using complete cases vs imputed data, and whether the correlation changes. *Summary box.*

## B. Data preprocessing
* **B1. Cleaning:** separating aggregates from countries, duplicates and non-finite checks, domain-range validation, flagging (not dropping) hyperinflation, missing-value strategy (interpolation ≤ 3 years, 10-year snapshot window, income-group median imputation for models, dropping < 60 % coverage indicators). Before/after counts table.
* **B2. Integration:** joining `Indicators` with `Country` (region, income group) and `Series` (names, topics).
* **B3. Transformation:** long → wide panel, log transform of skewed variables (GDP, CO₂), standardisation for clustering/PCA, growth rates.
* **B4. Reduction:** chunked filtering 1,344 → 32 indicators (5.66 M → 247 k rows), time-window snapshot, PCA (1 component = 63 % variance).
* **B5. Other:** feature exclusion of near-definitional variables (leakage control), coverage thresholds for trend plots.

## C. Data mining actions
1. Trend analysis by theme and income group/region (`04`–`10`).
2. Cross-country comparison, inequality (Gini, p90/p10) and β-convergence (`11`–`14`).
3. Regression: Preston curve, environmental Kuznets curve, life-expectancy model (`17`–`19`).
4. Model suite: 19 regressors × 6 theme targets, grouped CV, multiple seeds, feature importance.
5. Clustering: K-means (k by silhouette), PCA projection, comparison with GMM/Ward (`20`, `21`).
6. Case study: Vietnam vs regional peers (`15`).

## D. Metrics and evaluation
* Regression metrics: R², MAE, RMSE, cross-validation design (grouped by country so a country never appears in both train and test), mean ± std over seeds. Table of best model per theme from `results/summary_*.csv`, and linear vs non-linear comparison.
* Feature importance per theme.
* Clustering metrics: silhouette per k, agreement with World Bank income groups (74 %), cluster profiles.
* Statistical tests: β-convergence slope and p-value, Preston R².

## E. Interactive visualization web app (Streamlit)
What it is and how to run it, then one screenshot plus a short description per page: Overview, Trends, Compare (map, rankings, scatter), Models (live experiments), Clusters (choose method, k, seed), light/dark mode.

## F. Key findings and discussion
The 7 findings from `REPORT.md`, tightened.

## G. Limitations and future work

## H. Conclusion

## Appendix
Reproduction steps, file map, list of the 32 indicators with codes.

---
**Questions for you**
1. Markdown → PDF ok, or do you want LaTeX?
2. Should I add a cover page with group members and course name? If yes, send the names.

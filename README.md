# G2 Project Assignment: World Development Indicators analysis

End-to-end data-analytics project on the World Bank **World Development Indicators** (Kaggle `kaggle/world-development-indicators`, 1960–2015). It covers ETL, missing-data handling, EDA, theme trends, cross-country comparison, a multi-model evaluation suite, and an interactive Streamlit app.

![Overview page of the app](docs/screenshots/overview_light.png)

| | |
|---|---|
| ![Trends page: GDP per capita by income group](docs/screenshots/trends_light.png) | ![Compare page: world map of life expectancy](docs/screenshots/compare_light.png) |
| **Trends**: every indicator by income group or region | **Compare**: map, rankings, any-two-indicator scatter |
| ![Models page in dark mode: R² per theme](docs/screenshots/models_dark.png) | ![Clusters page in dark mode: PCA and world map](docs/screenshots/clusters_dark.png) |
| **Models**: 19 models, multi-seed R², live experiments | **Clusters**: K-means / GMM / Ward with your own k and seed |

<p align="center"><img src="docs/screenshots/overview_dark.png" alt="Overview page in dark mode" width="80%"><br><em>Light and dark mode, switchable from the top-right toggle.</em></p>

| File | Content |
|---|---|
| `WDI_Analysis.ipynb` | Main notebook, executed, with commentary in every section (writes `data/processed/`) |
| `REPORT.md` | Short written report with the key findings |
| `wdi/models.py` | Model suite: 19 regressors × 6 themes × N seeds, grouped CV, importance, trend predictions |
| `run_models.py` | CLI for the model suite, writes `results/` |
| `app.py` | Streamlit app: Overview, Trends, Compare, Models (incl. live experiments), Clusters; light/dark toggle top-right |
| `tests/test_models.py` | Smoke check for the model suite |
| `figures/` | Charts exported by the notebook |
| `results/` | Precomputed model results used by the app |
| `app_data/` | Gzipped processed data (1.5 MB) so the app runs without the raw Kaggle files |
| `data/` | Raw Kaggle CSVs and processed files (not committed, regenerate below) |

## Reproduce
```bash
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt        # Linux/macOS: .venv/bin/pip
# 1. data + notebook (needs a Kaggle API token in ~/.kaggle/kaggle.json)
.venv/Scripts/kaggle datasets download -d kaggle/world-development-indicators --unzip -p data/raw
.venv/Scripts/jupyter nbconvert --to notebook --execute --inplace WDI_Analysis.ipynb
# 2. model suite
.venv/Scripts/python run_models.py --mode snapshot --seeds 0 1 2 3 4
.venv/Scripts/python run_models.py --mode panel                      # slower, ~1 h on a laptop
.venv/Scripts/python tests/test_models.py
# 3. app
.venv/Scripts/streamlit run app.py
```
Only `Country.csv`, `Series.csv` and `Indicators.csv` are used; `database.sqlite` (1.4 GB) can be deleted.

## Model suite
Each theme gets one target that the other indicators try to explain:

| Theme | Target |
|---|---|
| Economy | GDP per capita (log) |
| Demography | fertility |
| Health | life expectancy |
| Education | secondary enrolment |
| Environment | CO₂ per capita (log) |
| Technology | internet users |

Near-definitional indicators are excluded as features. For example, infant and under-5 mortality are excluded when the target is life expectancy.

**Models:** Linear, Ridge, Lasso, ElasticNet, BayesianRidge, Huber, KNN, SVR, DecisionTree, RandomForest, ExtraTrees, GradientBoosting, HistGB, AdaBoost, MLP, XGBoost, LightGBM, Voting and Stacking.

**Evaluation:** grouped K-fold by country (a country is never in both train and test). It is repeated over several seeds and reported as mean ± std of R², MAE and RMSE.

| Option | Values |
|---|---|
| `--mode` | `snapshot` (latest value per country) / `panel` (country-years 1990–2014, more rows) |
| `--seeds` | any list, e.g. `0 1 2 42` |
| `--folds` | CV folds |
| `--impute` | `median` / `knn` / `iterative` |
| `--min-coverage` | drop sparse features |
| `--models`, `--themes` | subsets |
| `--no-year` | panel only: drop Year as a feature |

## Deploy (free)
**Streamlit Community Cloud:** push the repo to GitHub, open share.streamlit.io, choose the repo and set `app.py` as the entry point. The app reads `app_data/` and `results/`, so the raw data is not needed. The maps load Plotly's world shapes from its CDN.

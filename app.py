"""World Development Indicators: interactive explorer and model lab.  Run: streamlit run app.py"""
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score

from wdi.models import MODEL_NAMES, THEMES, Config, data_path, evaluate, summarise, trends
from wdi.story import CLUSTER_VARS, cluster_matrix, fit_clusters

st.set_page_config(page_title="World Development", page_icon="🌍", layout="wide")
RESULTS = Path(__file__).parent / "results"

# ---------------------------------------------------------------- design system
# Apple-style light and dark palettes. The toggle (top-right) stores its value in session state;
# Streamlit reruns the script on change, so every colour below is recomputed for the new mode.
MODES = {
    False: dict(bg="#f5f5f7", card="#ffffff", ink="#1d1d1f", grey="#6e6e73", line="#d2d2d7", grid="#f0f0f2",
                field="#ffffff", blue="#0071e3", soft="#a1c4f5", shadow="rgba(0,0,0,.05)", template="plotly_white"),
    True:  dict(bg="#000000", card="#1c1c1e", ink="#f5f5f7", grey="#a1a1a6", line="#38383a", grid="#2c2c2e",
                field="#2c2c2e", blue="#0a84ff", soft="#1f4f8a", shadow="rgba(0,0,0,.6)", template="plotly_dark"),
}
DARK = st.session_state.get("dark", False)
C = MODES[DARK]
BLUE, INK, GREY, LINE = C["blue"], C["ink"], C["grey"], C["line"]
FONT = '-apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", Inter, "Helvetica Neue", Arial, sans-serif'
INCOME_ORDER = ["Low income", "Lower middle income", "Upper middle income", "High income"]
INCOME_COLORS = dict(zip(INCOME_ORDER, ["#ff453a", "#ff9f0a", "#30b0c7", BLUE]))
CLUSTER_COLORS = ["#ff453a", "#ff9f0a", "#34c759", "#30b0c7", BLUE, "#5e5ce6", "#bf5af2", GREY]
PALETTE = [BLUE, "#ff9f0a", "#34c759", "#ff375f", "#5e5ce6", "#30b0c7", "#bf5af2", "#a2845e"]
px.defaults.color_discrete_sequence = PALETTE

st.markdown(f"""
<style>
@import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap");
html, body, [class*="css"], .stMarkdown, button, input, select, textarea {{ font-family: {FONT} !important; }}
.block-container {{ padding-top: 2.2rem; max-width: 1240px; }}
h1, h2, h3 {{ color: {INK}; letter-spacing: -0.02em; }}
.hero {{ text-align: center; padding: 2.5rem 1rem 1.5rem; }}
.hero .eyebrow {{ color: {BLUE}; font-weight: 600; font-size: 1.05rem; margin-bottom: .4rem; }}
.hero h1 {{ font-size: clamp(2.2rem, 5vw, 3.8rem); font-weight: 700; line-height: 1.05; margin: 0; }}
.hero p {{ color: {GREY}; font-size: clamp(1.05rem, 2vw, 1.35rem); max-width: 760px; margin: 1rem auto 0; }}
.section-title {{ font-size: 2rem; font-weight: 700; letter-spacing: -0.02em; margin: .4rem 0 .2rem; }}
.section-sub {{ color: {GREY}; font-size: 1.08rem; margin-bottom: 1.2rem; }}
.tile {{ background: {C["card"]}; border-radius: 20px; padding: 1.4rem 1.5rem; box-shadow: 0 2px 14px {C["shadow"]}; height: 100%; }}
.tile .k {{ color: {GREY}; font-size: .9rem; font-weight: 500; }}
.tile .v {{ color: {INK}; font-size: 2.3rem; font-weight: 700; letter-spacing: -0.02em; line-height: 1.15; }}
.tile .s {{ color: {GREY}; font-size: .85rem; }}
.insight {{ background: {C["card"]}; border-radius: 20px; padding: 1.3rem 1.5rem; box-shadow: 0 2px 14px {C["shadow"]};
            margin-bottom: 1rem; height: 100%; }}
.insight b {{ display: block; font-size: 1.12rem; margin-bottom: .35rem; color: {INK}; }}
.insight span {{ color: {GREY}; font-size: .98rem; line-height: 1.5; }}
div[data-testid="stPlotlyChart"], .tbl {{ background: {C["card"]}; border-radius: 20px;
            padding: .6rem; box-shadow: 0 2px 14px {C["shadow"]}; }}
.section-title {{ color: {INK}; }}
/* HTML tables (st.dataframe is canvas-drawn and cannot follow a custom theme) */
.tbl {{ overflow-x: auto; padding: .4rem .8rem; }}
.tbl table {{ border-collapse: collapse; width: 100%; font-size: .9rem; color: {INK}; }}
.tbl th {{ color: {GREY}; font-weight: 500; text-align: right; padding: .55rem .7rem; border-bottom: 1px solid {LINE}; }}
.tbl th.row_heading {{ text-align: left; }}
.tbl td {{ text-align: right; padding: .5rem .7rem; border-bottom: 1px solid {C["grid"]}; font-variant-numeric: tabular-nums; }}
.tbl tr:last-child td {{ border-bottom: 0; }}
/* theme toggle pinned to the top bar */
.st-key-dark {{ position: fixed; top: .8rem; right: 1.4rem; z-index: 1000001; width: auto !important; }}
/* Streamlit chrome and widgets */
.stApp, header[data-testid="stHeader"] {{ background: {C["bg"]}; }}
.stApp, .stMarkdown, [data-testid="stWidgetLabel"] p, [data-testid="stMarkdownContainer"] p,
[data-testid="stCaptionContainer"], .st-key-dark p {{ color: {INK}; }}
[data-testid="stCaptionContainer"] {{ color: {GREY} !important; }}
.stSelectbox [role="group"], .stMultiSelect [role="group"], .stTextInput input, .stNumberInput input,
.stNumberInput button, div[data-baseweb="input"] {{ background: {C["field"]} !important; color: {INK} !important;
            border-color: {LINE} !important; }}
[role="combobox"], .stSelectbox svg, .stMultiSelect svg, .stNumberInput svg {{ color: {INK} !important; }}
[data-testid="stSelectboxVirtualDropdown"], [role="listbox"] {{ background: {C["card"]} !important; color: {INK} !important;
            border-color: {LINE} !important; }}
[role="option"] {{ color: {INK} !important; }}
[role="option"]:hover, [role="option"][data-focused="true"] {{ background: {C["grid"]} !important; }}
[data-tag] {{ background: {BLUE} !important; color: #fff !important; }}
[data-tag] * {{ color: #fff !important; }}
[data-testid="stSliderThumbValue"], [data-testid="stSliderTickBarMin"], [data-testid="stSliderTickBarMax"] {{ color: {GREY}; }}
[data-testid="stForm"] {{ border-color: {LINE}; background: {C["card"]}; border-radius: 20px; }}
[data-testid="stAlert"] {{ background: {C["card"]}; color: {INK}; border-radius: 16px; }}
button[data-variant="segmented_control"] {{ background: {C["field"]}; color: {INK}; border-color: {LINE}; }}
button[data-variant="segmented_control"][data-selected="true"], button[data-variant="segmented_control"][aria-checked="true"] {{ background: {BLUE}; color: #fff; border-color: {BLUE}; }}
[data-testid="stTopNavLinkContainer"] span, header a span {{ color: {INK} !important; }}
[data-testid="stTooltipIcon"] svg {{ color: {GREY}; }}
.stButton > button, .stFormSubmitButton > button {{ background: {BLUE}; color: #fff; border: 0; border-radius: 980px; padding: .55rem 1.4rem; font-weight: 500; }}
.stButton > button:hover, .stFormSubmitButton > button:hover {{ background: #0077ed; color: #fff; }}
div[data-baseweb="select"] > div, .stNumberInput input {{ border-radius: 12px !important; }}
footer, #MainMenu {{ visibility: hidden; }}
</style>""", unsafe_allow_html=True)


def style(fig, h=420, legend=True):
    fig.update_layout(template=C["template"], height=h, font=dict(family=FONT, color=INK, size=13),
                      margin=dict(l=10, r=10, t=50, b=10), paper_bgcolor=C["card"], plot_bgcolor=C["card"],
                      title_font=dict(size=17, weight=600), colorway=PALETTE, showlegend=legend,
                      legend=dict(orientation="h", y=-0.18, title=None),
                      hoverlabel=dict(font_family=FONT, bgcolor=C["card"], font_color=INK))
    fig.update_xaxes(showgrid=False, linecolor=LINE)
    fig.update_yaxes(gridcolor=C["grid"], zeroline=False, linecolor=LINE)
    if any(t.type == "choropleth" for t in fig.data):
        fig.update_geos(bgcolor=C["card"], landcolor=C["grid"], showland=True, lakecolor=C["card"])
    return fig


def hero(eyebrow, title, sub):
    st.markdown(f'<div class="hero"><div class="eyebrow">{eyebrow}</div><h1>{title}</h1><p>{sub}</p></div>',
                unsafe_allow_html=True)


def section(title, sub=""):
    st.markdown(f'<div class="section-title">{title}</div><div class="section-sub">{sub}</div>', unsafe_allow_html=True)


def table(styler):
    """Theme-aware HTML table from a pandas Styler."""
    st.markdown(f'<div class="tbl">{styler.to_html()}</div>', unsafe_allow_html=True)


def tiles(items):
    for col, (k, v, s) in zip(st.columns(len(items)), items):
        col.markdown(f'<div class="tile"><div class="k">{k}</div><div class="v">{v}</div><div class="s">{s}</div></div>',
                     unsafe_allow_html=True)


# ---------------------------------------------------------------- data
LABELS = {
    "gdp_pc": "GDP per capita (const. 2005 US$)", "gdp_pc_ppp": "GDP per capita, PPP", "gdp_growth": "GDP growth (%)",
    "inflation": "Inflation (%)", "unemployment": "Unemployment (%)", "trade_open": "Trade (% of GDP)",
    "gini": "Gini index", "poverty_190": "Poverty at $1.90/day (%)", "population": "Population",
    "pop_growth": "Population growth (%)", "urban": "Urban population (%)", "fertility": "Fertility (births per woman)",
    "age65": "Population 65+ (%)", "age0_14": "Population 0–14 (%)", "female_lfp": "Female labour participation (%)",
    "life_exp": "Life expectancy (years)", "infant_mort": "Infant mortality (per 1,000)",
    "u5_mort": "Under-5 mortality (per 1,000)", "health_exp": "Health spending (% GDP)",
    "safe_water": "Improved water access (%)", "enrol_primary": "Primary enrolment (gross %)",
    "enrol_secondary": "Secondary enrolment (gross %)", "enrol_tertiary": "Tertiary enrolment (gross %)",
    "literacy": "Adult literacy (%)", "edu_exp": "Education spending (% GDP)", "co2_pc": "CO₂ per capita (t)",
    "energy_pc": "Energy use per capita (kg oil eq.)", "forest": "Forest area (% land)",
    "renewables": "Renewables (% final energy)", "electricity": "Electricity access (%)",
    "internet": "Internet users (per 100)", "mobile": "Mobile subscriptions (per 100)",
}
THEME_VARS = {
    "Economy": ["gdp_pc", "gdp_pc_ppp", "gdp_growth", "inflation", "unemployment", "trade_open", "gini", "poverty_190"],
    "Demography": ["population", "pop_growth", "urban", "fertility", "age65", "age0_14", "female_lfp"],
    "Health": ["life_exp", "infant_mort", "u5_mort", "health_exp", "safe_water"],
    "Education": ["enrol_primary", "enrol_secondary", "enrol_tertiary", "literacy", "edu_exp"],
    "Environment": ["co2_pc", "energy_pc", "forest", "renewables"],
    "Technology": ["electricity", "internet", "mobile"],
}
LOG_SCALE = {"gdp_pc", "gdp_pc_ppp", "population", "co2_pc", "energy_pc", "u5_mort", "infant_mort"}


@st.cache_data
def load_data():
    panel = pd.read_csv(data_path("wdi_panel_wide.csv"))
    snap = pd.read_csv(data_path("wdi_snapshot_2005_2014.csv"))
    for d in (panel, snap):
        d["Income"] = pd.Categorical(d["Income"], INCOME_ORDER, ordered=True)
    return panel, snap


def load_results(name):
    p = RESULTS / name
    # keyed on modification time so a fresh run_models.py output is picked up without restarting
    return _read_results(p, p.stat().st_mtime) if p.exists() else None


@st.cache_data
def _read_results(path, mtime):
    return pd.read_csv(path)


panel, snap = load_data()


def group_trend(var, by, min_share=0.3):
    g = panel.groupby([by, "Year"], observed=True)[var]
    size = panel.groupby(by, observed=True)["CountryCode"].nunique()
    out = pd.DataFrame({"median": g.median(), "n": g.count()}).reset_index()
    out = out[out["n"] / out[by].map(size).astype(float) >= min_share]
    return out


# ---------------------------------------------------------------- pages
def page_overview():
    hero("World Development Indicators · 1960–2014", "Fifty years of development,<br>in one place.",
         "Explore how 214 countries changed across the economy, demography, health, education, the environment "
         "and technology, and see how well 19 machine-learning models explain those differences.")
    s = load_results("summary_panel.csv")
    best = f"{s.groupby('theme').r2_mean.max().mean():.2f}" if s is not None else "–"
    tiles([("Countries", "214", "plus 33 regional aggregates"), ("Indicators", "32", "selected from 1,344 series"),
           ("Years", "55", "1960 – 2014"), ("Models", str(len(MODEL_NAMES)), f"mean best R² across themes: {best}")])
    st.write("")
    le = group_trend("life_exp", "Income")
    fig = px.line(le, x="Year", y="median", color="Income", color_discrete_map=INCOME_COLORS,
                  category_orders={"Income": INCOME_ORDER}, title="Life expectancy, median by income group",
                  labels={"median": "years"})
    fig.update_traces(line_width=3)
    st.plotly_chart(style(fig, 440), width="stretch", theme=None)
    insights = [
        ("Health converged.", "The life-expectancy gap between high- and low-income countries fell from 30 to 21 years."),
        ("Income did not.", "Income inequality between countries barely moved: the top/bottom decile ratio is still ~80×."),
        ("Policy shifts the curve.", "At US$1,000 per head, life expectancy rose ~5 years since 1990. Vietnam lives 10 years longer than its income predicts."),
        ("Growth still means CO₂.", "CO₂ per capita tracks income as tightly as health does (ρ = 0.86)."),
    ]
    for row in (insights[:2], insights[2:]):  # row by row so phones stack them in reading order
        for col, (b, t) in zip(st.columns(2), row):
            col.markdown(f'<div class="insight"><b>{b}</b><span>{t}</span></div>', unsafe_allow_html=True)


def page_trends():
    section("Theme trends", "Median across countries, shown only when at least 30% of the group reports.")
    c1, c2, c3 = st.columns([1, 2, 1])
    theme = c1.selectbox("Theme", list(THEME_VARS))
    var = c2.selectbox("Indicator", THEME_VARS[theme], format_func=LABELS.get)
    by = c3.segmented_control("Group by", ["Income", "Region"], default="Income") or "Income"
    t = group_trend(var, by)
    fig = px.line(t, x="Year", y="median", color=by, log_y=var in LOG_SCALE, title=LABELS[var],
                  color_discrete_map=INCOME_COLORS if by == "Income" else None,
                  category_orders={"Income": INCOME_ORDER}, labels={"median": ""})
    fig.update_traces(line_width=3)
    st.plotly_chart(style(fig, 460), width="stretch", theme=None)

    section("Country explorer", "Compare individual countries on the same indicator.")
    names = sorted(panel.ShortName.dropna().unique())
    pick = st.multiselect("Countries", names, default=["Vietnam", "China", "Thailand", "Indonesia", "India"])
    d = panel[panel.ShortName.isin(pick)].dropna(subset=[var])
    fig = px.line(d, x="Year", y=var, color="ShortName", log_y=var in LOG_SCALE, labels={var: "", "ShortName": ""},
                  title=LABELS[var])
    fig.update_traces(line_width=2.5)
    st.plotly_chart(style(fig, 420), width="stretch", theme=None)


def page_compare():
    section("Compare countries", "Latest available value between 2005 and 2014.")
    c1, c2 = st.columns([2, 1])
    var = c1.selectbox("Indicator", list(LABELS), index=list(LABELS).index("life_exp"), format_func=LABELS.get)
    n = c2.slider("Top / bottom", 5, 20, 10)
    d = snap.dropna(subset=[var])
    color = np.log10(d[var].clip(lower=1e-3)) if var in LOG_SCALE else d[var]
    fig = go.Figure(go.Choropleth(locations=d.CountryCode, z=color, text=d.ShortName, colorscale="Blues",
                                  customdata=d[var], hovertemplate="%{text}<br>%{customdata:,.2f}<extra></extra>",
                                  marker_line_color=C["card"], marker_line_width=0.4,
                                  colorbar=dict(title="log₁₀" if var in LOG_SCALE else "", thickness=10)))
    fig.update_geos(showframe=False, showcoastlines=False, projection_type="natural earth",
                    projection_rotation_lon=0, lonaxis_range=[-180, 180], lataxis_range=[-58, 85])
    st.plotly_chart(style(fig, 480, legend=False).update_layout(title=LABELS[var]), width="stretch", theme=None)
    s = d.sort_values(var)
    a, b = st.columns(2)
    for col, part, title in ((a, s.head(n), "Lowest"), (b, s.tail(n), "Highest")):
        fig = px.bar(part, x=var, y="ShortName", orientation="h", color="Income", color_discrete_map=INCOME_COLORS,
                     category_orders={"Income": INCOME_ORDER}, labels={var: "", "ShortName": ""}, title=f"{title} {n}")
        col.plotly_chart(style(fig, 120 + 28 * n), width="stretch", theme=None)

    section("Relationship explorer", "Any two indicators, one bubble per country (size = population).")
    c1, c2 = st.columns(2)
    x = c1.selectbox("X axis", list(LABELS), index=list(LABELS).index("gdp_pc"), format_func=LABELS.get)
    y = c2.selectbox("Y axis", list(LABELS), index=list(LABELS).index("life_exp"), format_func=LABELS.get)
    d = snap.dropna(subset=[x, y, "population"])
    fig = px.scatter(d, x=x, y=y, size="population", color="Region", hover_name="ShortName", size_max=45,
                     log_x=x in LOG_SCALE, log_y=y in LOG_SCALE, labels={x: LABELS[x], y: LABELS[y]})
    st.plotly_chart(style(fig, 520), width="stretch", theme=None)
    st.caption(f"Spearman ρ = {d[x].corr(d[y], method='spearman'):.2f} across {len(d)} countries")


def page_models():
    section("Model lab", "19 regressors, one target per theme, grouped cross-validation by country, averaged over seeds.")
    mode = st.segmented_control("Results", ["panel", "snapshot"], default="panel",
                                format_func={"panel": "Country-years 1990–2014", "snapshot": "Latest snapshot"}.get) or "panel"
    summary, metrics = load_results(f"summary_{mode}.csv"), load_results(f"metrics_{mode}.csv")
    if summary is None:
        st.info("No precomputed results yet. Run `python run_models.py` or use the live lab below.")
    else:
        targets = {t: LABELS[v["target"]] + (" (log)" if v["log"] else "") for t, v in THEMES.items()}
        best = summary.sort_values("r2_mean", ascending=False).groupby("theme").head(1).set_index("theme")
        tiles([(t, f"{best.loc[t, 'r2_mean']:.2f}", f"{best.loc[t, 'model']} · {targets[t]}")
               for t in THEMES if t in best.index][:3])
        st.write("")
        tiles([(t, f"{best.loc[t, 'r2_mean']:.2f}", f"{best.loc[t, 'model']} · {targets[t]}")
               for t in THEMES if t in best.index][3:])
        st.write("")
        theme = st.selectbox("Theme", list(THEMES), format_func=lambda t: f"{t}: {targets[t]}")
        s = summary[summary.theme == theme].sort_values("r2_mean")
        fig = go.Figure(go.Bar(x=s.r2_mean, y=s.model, orientation="h", error_x=dict(array=s.r2_std, color=GREY),
                               marker_color=[BLUE if m == s.model.iloc[-1] else C["soft"] for m in s.model],
                               hovertemplate="%{y}: R² %{x:.3f}<extra></extra>"))
        fig.update_xaxes(range=[max(0, s.r2_mean.min() - 0.1), 1])
        a, b = st.columns([3, 2])
        a.plotly_chart(style(fig, 620, legend=False).update_layout(title="Cross-validated R², mean ± std over seeds"),
                       width="stretch", theme=None)
        m = metrics[metrics.theme == theme]
        fig = px.strip(m, x="r2", y="model", category_orders={"model": s.model.tolist()[::-1]},
                       title="Seed-to-seed spread", labels={"r2": "R²", "model": ""})
        b.plotly_chart(style(fig, 620, legend=False), width="stretch", theme=None)

        imp = load_results(f"importance_{mode}.csv")
        tr = load_results("trends_income.csv") if mode == "panel" else None
        a, b = st.columns(2) if tr is not None else (None, st.container())
        if tr is not None:
            t = tr[tr.theme == theme]
            fig = go.Figure()
            for inc in INCOME_ORDER:
                g = t[t.Income == inc]
                fig.add_scatter(x=g.Year, y=g.actual, name=inc, line=dict(color=INCOME_COLORS[inc], width=3))
                fig.add_scatter(x=g.Year, y=g.pred, name=f"{inc} · models", showlegend=False,
                                line=dict(color=INCOME_COLORS[inc], width=2, dash="dot"))
            fig.update_layout(title="Actual (solid) vs mean of all models (dotted)")
            if THEMES[theme]["log"]:
                fig.update_yaxes(type="log")
            a.plotly_chart(style(fig, 440), width="stretch", theme=None)
        if imp is not None:
            i = imp[imp.theme == theme].head(12).iloc[::-1]
            fig = px.bar(i, x="importance", y=i.feature.map(lambda f: LABELS.get(f, f)), orientation="h",
                         error_x="std", title=f"What drives it? Permutation importance ({i.model.iloc[0]})",
                         labels={"y": "", "importance": "drop in R² when shuffled"})
            fig.update_traces(marker_color=BLUE)
            b.plotly_chart(style(fig, 440, legend=False), width="stretch", theme=None)

    section("Run your own experiment", "Choose models, seeds and settings. Results are computed live and cached.")
    with st.form("lab"):
        c1, c2, c3 = st.columns(3)
        themes = c1.multiselect("Themes", list(THEMES), default=["Health"])
        models = c2.multiselect("Models", MODEL_NAMES, default=["Ridge", "RandomForest", "LightGBM", "SVR"])
        lmode = c3.selectbox("Data", ["snapshot", "panel"], format_func={"panel": "Country-years 1990–2014",
                                                                       "snapshot": "Latest snapshot (fast)"}.get)
        c1, c2, c3, c4 = st.columns(4)
        seeds = c1.text_input("Seeds", "0, 1, 2", help="Comma-separated, e.g. 0, 1, 2, 42")
        folds = c2.slider("CV folds", 3, 10, 5)
        impute = c3.selectbox("Imputer", ["median", "knn", "iterative"])
        cov = c4.slider("Min. feature coverage", 0.3, 0.9, 0.5, 0.05)
        go_ = st.form_submit_button("Run experiment")
    if go_:
        try:
            seed_list = [int(x) for x in seeds.replace(" ", "").split(",") if x]
        except ValueError:
            st.error("Seeds must be whole numbers separated by commas.")
            return
        if not (themes and models and seed_list):
            st.warning("Pick at least one theme, one model and one seed.")
            return
        if lmode == "panel" and ("Stacking" in models or len(models) * len(seed_list) * len(themes) > 30):
            st.caption("Panel mode with many models (or Stacking) can take several minutes.")
        res = run_live(tuple(themes), tuple(models), tuple(seed_list), folds, lmode, impute, cov)
        s = summarise(res)
        fig = px.bar(s, x="r2_mean", y="model", color="theme", error_x="r2_std", barmode="group", orientation="h",
                     labels={"r2_mean": "R² (mean ± std)", "model": ""}, title="Your experiment",
                     category_orders={"model": s.groupby("model").r2_mean.mean().sort_values(ascending=False).index.tolist()})
        fig.update_xaxes(range=[max(0, s.r2_mean.min() - 0.1), 1])
        st.plotly_chart(style(fig, 160 + 34 * len(s)), width="stretch", theme=None)
        table(s.style.format(precision=4).hide(axis="index"))


@st.cache_data(show_spinner=False)
def run_live(themes, models, seeds, folds, mode, impute, cov):
    bar = st.progress(0.0, "Training…")
    cfg = Config(themes=list(themes), models=list(models), seeds=list(seeds), folds=folds, mode=mode,
                 impute=impute, min_coverage=cov)
    metrics, _ = evaluate(cfg, lambda i, n, r: bar.progress(i / n, f"{r['theme']} · {r['model']} · seed {r['seed']}"))
    bar.empty()
    return metrics


def page_clusters():
    section("Development profiles", "Unsupervised clustering on 15 standardised indicators, projected with PCA.")
    vars_ = CLUSTER_VARS
    c1, c2, c3 = st.columns(3)
    algo = c1.selectbox("Algorithm", ["K-means", "Gaussian mixture", "Agglomerative (Ward)"])
    k = c2.slider("Clusters (k)", 2, 8, 4)
    seed = c3.number_input("Seed", 0, 10_000, 42)
    d, X, Z = cluster_matrix(snap)
    lab = fit_clusters(Z, X.gdp_pc, algo, k, seed)
    d["Cluster"] = pd.Series(lab).map(lambda c: f"Cluster {c}")
    pcs = PCA(2, random_state=seed).fit(Z)
    P = pcs.transform(Z)
    if np.corrcoef(P[:, 0], X["gdp_pc"])[0, 1] < 0:
        P[:, 0] *= -1
    tiles([("Countries", str(len(d)), "with ≥70% of indicators"),
           ("Silhouette", f"{silhouette_score(Z, lab):.2f}", "−1 to 1, higher = better separated"),
           ("PC1 explains", f"{pcs.explained_variance_ratio_[0]:.0%}", "of variance: overall development"),
           ("Agreement", f"{pd.crosstab(d.Cluster, d.Income).max(axis=1).sum() / len(d):.0%}", "best match with WB income groups")])
    st.write("")
    cats = sorted(d.Cluster.unique())
    a, b = st.columns(2)
    fig = px.scatter(d.assign(PC1=P[:, 0], PC2=P[:, 1]), x="PC1", y="PC2", color="Cluster", hover_name="ShortName",
                     category_orders={"Cluster": cats}, title="Countries in PCA space",
                     color_discrete_sequence=CLUSTER_COLORS)
    fig.update_traces(marker=dict(size=9, line=dict(width=0.5, color=C["card"])))
    a.plotly_chart(style(fig, 460), width="stretch", theme=None)
    fig = px.choropleth(d, locations="CountryCode", color="Cluster", hover_name="ShortName",
                        category_orders={"Cluster": cats}, title="Where the clusters are",
                        color_discrete_sequence=CLUSTER_COLORS)
    fig.update_geos(showframe=False, showcoastlines=False, projection_type="natural earth", projection_rotation_lon=0,
                    lonaxis_range=[-180, 180], lataxis_range=[-58, 85])
    b.plotly_chart(style(fig, 460), width="stretch", theme=None)
    prof = snap.set_index("CountryCode").loc[d.CountryCode, vars_].groupby(d.Cluster.values).median().T
    prof.index = prof.index.map(LABELS)
    table(prof.style.format("{:,.1f}").background_gradient(cmap="Blues", axis=1))


nav = st.navigation([st.Page(page_overview, title="Overview", default=True),
                     st.Page(page_trends, title="Trends", url_path="trends"),
                     st.Page(page_compare, title="Compare", url_path="compare"),
                     st.Page(page_models, title="Models", url_path="models"),
                     st.Page(page_clusters, title="Clusters", url_path="clusters")], position="top")
st.toggle("Dark mode", key="dark")
nav.run()

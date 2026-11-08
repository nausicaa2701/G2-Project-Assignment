"""Data pages: A · Initial data exploration (A1-A3) and B · Data preprocessing (B1-B4).

Every number is recomputed from app_data/ through wdi/story/explore.py, except the raw-file figures, which come
from the notebook's ETL log because the 574 MB raw files are not shipped with the app.
"""
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from ui import core as k
from ui.core import (INCOME_ORDER, LABELS, LOG_SCALE, THEME_VARS, VN, VN_COLOR, bridge, chart, group_trend,
                     hero, insights, method_box, panel, section, snap, table, takeaway, tiles)
from wdi.models import THEMES
from wdi.story import explore as ex
from wdi.story.part3 import CLUSTER_LOG, CLUSTER_VARS, cluster_matrix

THEME_OF = {v: t for t, vs in THEME_VARS.items() for v in vs}
SKEWED = sorted(LOG_SCALE | {"trade_open"})


def _short(v):
    return LABELS.get(v, v).split(" (")[0]


@st.cache_data(show_spinner=False)
def _a_results():
    s, p = ex.snapshot(), ex.panel()
    corr = ex.missing_corr_impact(s)
    return dict(stats=ex.summary_stats(s), impact=ex.missing_impact(s), corr=corr, corr_attrs=dict(corr.attrs),
                outliers=ex.outliers(s), years=ex.obs_per_year(p), decade=ex.coverage_by_decade(p),
                hyper=ex.hyperinflation(p))


@st.cache_data(show_spinner=False)
def _b_results():
    s, p = ex.snapshot(), ex.panel()
    var, load = ex.pca_variance(s)
    return dict(valid=ex.validation(p), cov=ex.coverage_table(s), sizes=ex.sample_sizes(s), skew=ex.skew_transform(s),
                pca_var=var, pca_load=load)


def _pca_coords():
    d, X, Z = cluster_matrix(snap.assign(Income=snap.Income.astype(str)))
    from sklearn.decomposition import PCA
    pca = PCA(2).fit(Z)
    P = pca.transform(Z)
    if np.corrcoef(P[:, 0], X.gdp_pc)[0, 1] < 0:
        P[:, 0] *= -1
    return d.assign(PC1=P[:, 0], PC2=P[:, 1]), pca.explained_variance_ratio_


# A · exploration
def page_a():
    r = _a_results()
    hero("A · Initial data exploration", "What is in the data,<br>and what is missing.",
         "Size and attributes of the World Bank files, summary statistics of the 32 indicators we kept, "
         "and the outliers, groups and values that stand out. Missing values are checked at every step.")

    # A1
    section("A1 · Dataset overview", "The raw Kaggle files, their attributes, and the subset analysed in this project.")
    tiles([("Raw observations", "5.66 M", "Indicators.csv, one row per country × indicator × year"),
           ("Economies", "247", "214 countries + 33 aggregates"),
           ("Indicators", "1,344", "1960–2015, 574 MB on disk"),
           ("Analysed", f"{len(panel):,} × 32", f"country-years × indicators; snapshot {len(snap)} × 32")])
    st.write("")
    st.markdown("**Raw files**")
    f = ex.RAW_FILES.copy()
    f["rows"] = f.rows.map(lambda v: f"{v:,.0f}" if pd.notna(v) else "–")
    f["columns"] = f["columns"].map(lambda v: f"{v:.0f}" if pd.notna(v) else "–")
    table(f.style.hide(axis="index"))
    st.markdown("**Attributes of the raw tables**")
    table(ex.RAW_ATTRIBUTES.style.hide(axis="index"))

    y = r["years"]
    first, peak = y.iloc[0], y.loc[y.cells.idxmax()]
    takeaway(f"The table gets denser over time: <em>{first.cells:,}</em> values in {first.Year:.0f}, "
             f"<em>{peak.cells:,}</em> in {peak.Year:.0f}",
             "Non-empty cells of the 32 selected indicators per year (after cleaning). Many series only start in "
             "1990, and the last year is mostly empty because data arrives with a lag.")
    fig = go.Figure(go.Bar(x=y.Year, y=y.cells, marker_color=k.BLUE, customdata=y.countries,
                           hovertemplate="%{x}: %{y:,} values from %{customdata} countries<extra></extra>"))
    fig.update_yaxes(title="non-empty indicator values")
    chart(fig, 320, legend=False)

    num = ex.numeric(snap)
    attrs = pd.DataFrame({"Theme": [THEME_OF[v] for v in num.columns], "Attribute": num.columns,
                          "Meaning (unit)": [LABELS[v] for v in num.columns],
                          "Type": ["continuous, ratio scale"] * num.shape[1],
                          "Panel coverage": 100 * ex.numeric(panel)[num.columns].notna().mean().values,
                          "Snapshot coverage": 100 * num.notna().mean().values})
    method_box("The 32 attributes kept for analysis, chosen for relevance to development, coverage and "
               "comparability. Each becomes a numeric column of the country-year **panel** (1960–2015) and of the "
               "**snapshot** (latest value per country in 2005–2014, so each country counts once). The categorical "
               "attributes are `Region` (nominal, 7 values) and `Income` (ordinal, 4 levels).",
               "The 32 selected attributes",
               attrs.style.format({"Panel coverage": "{:.0f} %", "Snapshot coverage": "{:.0f} %"}).hide(axis="index"))

    # A2
    section("A2 · Summary statistics", "Snapshot: one value per country (latest in 2005–2014), so large and small "
            "countries count the same.")
    s = r["stats"]
    gdp = s.loc["gdp_pc"]
    takeaway(f"Income is strongly right-skewed: the mean GDP per head (<em>US${gdp['mean']:,.0f}</em>) is "
             f"<em>{gdp['mean'] / gdp['median']:.1f}×</em> the median",
             f"{int((s["skew"] > 1).sum())} of 32 attributes have skewness above 1, so medians and log scales describe "
             "them better than means. Percentages are bounded at 100 and skewed to the left.")
    theme = st.segmented_control("Theme", ["All"] + list(THEME_VARS), default="All", key="a2_theme") or "All"
    rows = s if theme == "All" else s.loc[[v for v in THEME_VARS[theme] if v in s.index]]
    t = rows.copy()
    t.index = [f"{_short(v)} · {v}" for v in t.index]
    table(t.style.format({"count": "{:.0f}", "missing_%": "{:.1f}", "skew": "{:.2f}"}, precision=2, thousands=",")
          .format(lambda v: f"{v:,.0f}" if abs(v) >= 1000 else f"{v:,.3g}",
                  subset=["mean", "median", "std", "min", "max"])
          .background_gradient(cmap="Oranges", subset=["missing_%"], vmin=0, vmax=60)
          .background_gradient(cmap="Purples", subset=["skew"], vmin=0, vmax=5))

    c1, c2 = st.columns([2, 1])
    var = c1.selectbox("Distribution of", list(num.columns), index=list(num.columns).index("gdp_pc"),
                       format_func=lambda v: LABELS[v], key="a2_var")
    x = snap[var].dropna()
    can_log = (x > 0).all()
    log = c2.segmented_control("Scale", ["raw", "log₁₀"], default="log₁₀" if var in LOG_SCALE else "raw",
                               key="a2_scale", disabled=not can_log) or "raw"
    xs = np.log10(x) if log == "log₁₀" and can_log else x
    a, b = st.columns(2)
    fig = px.histogram(xs, nbins=35, labels={"value": f"{LABELS[var]}{' (log₁₀)' if xs is not x else ''}"})
    fig.update_traces(marker_color=k.BLUE)
    for val, name, dash, pos in ((xs.mean(), "mean", "solid", "top right"), (xs.median(), "median", "dash", "top left")):
        fig.add_vline(x=val, line=dict(color=k.INK, dash=dash, width=1.5), annotation_text=name,
                      annotation_position=pos, annotation_font_color=k.INK)
    fig.update_layout(title=f"Skewness {xs.skew():+.2f} · n = {len(xs)} countries", yaxis_title="countries")
    chart(fig, 380, legend=False, target=a)
    d = snap.dropna(subset=[var])
    fig = px.box(d, x="Income", y=var, color="Income", points="outliers", hover_name="ShortName",
                 category_orders={"Income": INCOME_ORDER}, color_discrete_map=k.INCOME_COLORS,
                 log_y=log == "log₁₀" and can_log, labels={var: "", "Income": ""}, title="By income group")
    chart(fig, 380, legend=False, target=b)

    st.markdown("#### Missing values and their impact on the summary statistics")
    miss = 100 * ex.numeric(panel).isna().mean().mean()
    takeaway(f"<em>{miss:.0f} %</em> of panel cells are empty, and poorer countries report less: "
             "the gaps are not random",
             "Left: share of country-years with a value, per indicator and decade (structural gaps: many series "
             "start in 1990). Right: share of countries reporting in the snapshot, per income group.")
    a, b = st.columns(2)
    dec = r["decade"]
    fig = px.imshow(dec.values, x=[f"{c}s" for c in dec.columns], y=[_short(v) for v in dec.index],
                    color_continuous_scale="Blues", zmin=0, zmax=100, aspect="auto",
                    labels=dict(color="% reported"), title="Coverage by decade (panel)")
    chart(fig, 640, legend=False, target=a)
    cov = 100 * num.notna().groupby(snap.Income, observed=True).mean().reindex(INCOME_ORDER).T
    cov = cov.loc[cov.mean(axis=1).sort_values(ascending=False).index]
    fig = px.imshow(cov.values, x=["Low", "Lower-mid", "Upper-mid", "High"], y=[_short(v) for v in cov.index],
                    color_continuous_scale="Blues", zmin=0, zmax=100, aspect="auto",
                    labels=dict(color="% reported"), title="Coverage by income group (snapshot)")
    chart(fig, 640, legend=False, target=b)

    imp = r["impact"].copy()
    pov = imp.set_index("indicator").loc["poverty_190"]
    takeaway(f"Ignoring the gaps overstates world poverty: the mean falls from <em>{pov.mean_reporters:.1f} %</em> "
             f"to <em>{pov.mean_imputed:.1f} %</em> once non-reporting countries are counted",
             "Mean on reporting countries only vs after filling each gap with the median of the country's income "
             "group. Well-covered indicators barely move; survey indicators move a lot, in both directions.")
    imp = imp.sort_values("mean_shift_%")
    fig = go.Figure(go.Bar(x=imp["mean_shift_%"], y=[_short(v) for v in imp.indicator], orientation="h",
                           marker_color=[k.BLUE if abs(v) < 3 else "#ff9f0a" for v in imp["mean_shift_%"]],
                           text=[f"{v:+.1f} %" for v in imp["mean_shift_%"]], textposition="outside",
                           customdata=imp["missing_%"],
                           hovertemplate="%{y}: mean %{x:+.1f} % · %{customdata:.0f} % missing<extra></extra>"))
    fig.update_xaxes(title="change of the mean after imputation (orange: more than 3 %)",
                     range=[imp["mean_shift_%"].min() - 8, imp["mean_shift_%"].max() + 8])
    chart(fig, 380, legend=False)
    t = imp.set_index("indicator").drop(columns="n")
    t.index = t.index.map(_short)
    t.columns = ["missing %", "mean (reporters)", "mean (imputed)", "mean shift %", "median (reporters)",
                 "median (imputed)", "cov. LI", "cov. LMI", "cov. UMI", "cov. HI"]
    method_box("**Why it happens:** the World Bank does not measure extreme poverty in rich countries, so the "
               "reporters are mostly poor countries; literacy and child mortality are missing mostly for rich "
               "countries, so their reporting-only means are biased the other way.\n\n"
               "**Consequence for B:** indicators below 60 % coverage are left out of the exploration, gaps are "
               "imputed only where a method needs complete rows, and imputation is never used for correlations "
               "on sparse indicators.",
               "Impact table and reading", t.style.format(precision=1))

    # A3
    section("A3 · Outliers, groups and interesting values", "IQR rule on the analysis scale (log₁₀ for skewed "
            "indicators), correlation structure, and the values that stand out.")
    o = r["outliers"]
    n_out = int((o.n_outliers > 0).sum())
    hy = r["hyper"]
    takeaway(f"<em>{n_out} of 32</em> indicators have outliers, and almost all of them are real",
             f"Trade hubs, Gulf CO₂, war years and small islands, not data errors. They are kept; robust statistics "
             f"(median, Spearman, log scale) limit their weight. {len(hy)} hyperinflation years (> 500 %) are flagged.")
    cands = o[o.n_outliers > 0].sort_values("n_outliers", ascending=False).indicator.tolist()
    v = st.selectbox("Indicator", cands, index=cands.index("trade_open") if "trade_open" in cands else 0,
                     format_func=lambda c: f"{LABELS[c]} · {int(o.set_index('indicator').at[c, 'n_outliers'])} outliers",
                     key="a3_var")
    xs = snap.set_index("ShortName")[v].dropna()
    z, lo, hi, mask = ex.iqr_fences(xs, v in {"gdp_pc", "gdp_pc_ppp", "population", "co2_pc", "energy_pc",
                                              "u5_mort", "infant_mort"})
    rng = np.random.default_rng(1)
    jit = rng.uniform(-.3, .3, len(z))
    fig = go.Figure(go.Scatter(x=z[~mask], y=jit[~mask], mode="markers", text=z.index[~mask], name="within fences",
                               marker=dict(color=k.GREY, size=8, opacity=.45), hovertemplate="%{text}<extra></extra>"))
    top = z[mask].sub(z.median()).abs().sort_values(ascending=False).index[:5]
    fig.add_scatter(x=z[mask], y=jit[mask], mode="markers", name="outlier", text=z.index[mask],
                    marker=dict(color="#ff9f0a", size=11), hovertemplate="%{text}<extra></extra>")
    for i, c in enumerate(top):
        fig.add_annotation(x=z[c], y=jit[z.index.get_loc(c)], text=c, showarrow=False, yshift=12 if i % 2 else -12,
                           font=dict(color=k.INK, size=11))
    if "Vietnam" in z.index:
        fig.add_scatter(x=[z["Vietnam"]], y=[0], mode="markers+text", text=["Vietnam"], name="Vietnam",
                        textposition="bottom center", marker=dict(color=VN_COLOR, size=13),
                        textfont=dict(color=VN_COLOR))
    for f_, name in ((lo, "Q1 − 1.5 IQR"), (hi, "Q3 + 1.5 IQR")):
        fig.add_vline(x=f_, line=dict(color=k.INK, dash="dot"), annotation_text=name, annotation_font_color=k.GREY)
    fig.update_yaxes(visible=False, range=[-1, 1])
    fig.update_xaxes(title=f"{LABELS[v]}{' (log₁₀)' if z is not xs else ''}")
    chart(fig, 300)
    st.markdown("**Indicators with outliers** (the three most extreme countries each)")
    table(o[o.n_outliers > 0].sort_values("n_outliers", ascending=False)
          .assign(indicator=lambda d: d.indicator.map(_short)).style.hide(axis="index"))
    a, b = st.columns(2)
    with a:
        st.markdown(f"**Hyperinflation years** (> 500 %): {len(hy)} country-years in the panel")
        table(hy.head(8).drop(columns="CountryCode").style.format({"inflation": "{:,.0f} %", "Year": "{:.0f}"})
              .hide(axis="index"))
    with b:
        st.markdown("**Reading.** Small trading hubs have trade above 300 % of GDP, Gulf states very high CO₂, war "
                    "years produce GDP collapses, and gross enrolment above 100 % reflects over-age pupils. These are "
                    "real values, so they stay in the data. Hyperinflation years are flagged rather than deleted: "
                    "group statistics use medians and the models log-transform inflation, so they cannot dominate.")

    st.markdown("#### Groups of similar instances and attributes")
    cols = [c for c in num.columns if num[c].notna().mean() >= .6]
    rho = num[cols].corr(method="spearman")
    order = rho["gdp_pc"].sort_values(ascending=False).index
    rho = rho.loc[order, order]
    big = rho["gdp_pc"].drop("gdp_pc").abs()
    pts, ev = _pca_coords()
    takeaway(f"Indicators form one block around income, and countries lie on one axis: "
             f"<em>PC1 = {ev[0]:.0%}</em> of the variance",
             f"{int((big >= .7).sum())} indicators correlate with GDP per head at |ρ| ≥ 0.7. In PCA space, "
             "Sub-Saharan Africa forms the low end and oil exporters sit apart: rich, but with weaker health outcomes.")
    a, b = st.columns(2)
    fig = px.imshow(rho.values, x=[_short(c) for c in order], y=[_short(c) for c in order], zmin=-1, zmax=1,
                    color_continuous_scale="RdBu", aspect="auto", labels=dict(color="ρ"),
                    title="Spearman correlation, sorted by ρ with GDP per head")
    fig.update_xaxes(tickangle=-60, tickfont_size=9)
    fig.update_yaxes(tickfont_size=9)
    chart(fig, 620, legend=False, target=a)
    fig = px.scatter(pts, x="PC1", y="PC2", color="Region", hover_name="ShortName",
                     title=f"Countries in PCA space (15 indicators, {len(pts)} countries)",
                     labels={"PC1": f"PC1 · overall development ({ev[0]:.0%})", "PC2": f"PC2 ({ev[1]:.0%})"})
    fig.update_traces(marker=dict(size=8, opacity=.8))
    vn = pts[pts.CountryCode == VN]
    fig.add_scatter(x=vn.PC1, y=vn.PC2, mode="markers+text", text=["Vietnam"], textposition="top center",
                    marker=dict(color=VN_COLOR, size=15, line=dict(color=k.C["card"], width=2)),
                    textfont=dict(color=VN_COLOR, size=13), showlegend=False)
    chart(fig, 620, target=b)

    st.markdown("#### Interesting attributes and values")
    le = group_trend("life_exp", "Income").pivot(index="Year", columns="Income", values="median")
    gap0, gap1 = (le["High income"] - le["Low income"]).dropna().iloc[[0, -1]]
    fer = group_trend("fertility", "Region").pivot(index="Year", columns="Region", values="median")
    fer_chg = 100 * (fer.loc[2013] / fer.loc[1960] - 1)
    ssa = fer_chg["Sub-Saharan Africa"]
    others = fer_chg.drop(["Sub-Saharan Africa", "Europe & Central Asia", "North America"], errors="ignore")
    g = snap.gdp_pc.dropna()
    vns = snap.set_index("CountryCode").loc[VN]
    insights([
        ("Life expectancy converged.", f"The gap between high- and low-income countries fell from {gap0:.1f} to "
         f"{gap1:.1f} years. It is the most informative outcome and anchors Part 1."),
        ("Fertility splits off Sub-Saharan Africa.", f"It fell {abs(ssa):.0f} % there (1960–2013) against "
         f"{abs(others.max()):.0f}–{abs(others.min()):.0f} % in the other developing regions."),
        ("GDP per head spans three orders of magnitude.", f"From US${g.min():,.0f} to US${g.max():,.0f}; the "
         f"richest decile is {g.quantile(.9) / g.quantile(.1):.0f}× the poorest."),
        ("Vietnam is an interesting value everywhere.", f"GDP per head US${vns.gdp_pc:,.0f}, yet life expectancy "
         f"{vns.life_exp:.1f} years, about the level of countries several times richer (Part 2)."),
    ])

    st.markdown("#### Impact of missing values on the exploration")
    c = r["corr"].copy()
    att = r["corr_attrs"]
    gini = c.set_index("pair").loc["gdp_pc ~ gini"]
    takeaway(f"Imputation can change a conclusion: the Gini–income correlation moves from "
             f"<em>{gini.rho_pairwise:+.2f}</em> to <em>{gini.rho_imputed:+.2f}</em>",
             f"Dropping incomplete countries is worse: only {att['listwise_n_all32']} of 214 countries report all "
             f"32 indicators ({att['listwise_n_15cluster']} for the 15 clustering ones), mostly rich ones.")
    a, b = st.columns(2)
    fig = go.Figure()
    for _, row in c.iterrows():
        fig.add_scatter(x=[row.rho_pairwise, row.rho_imputed], y=[row.pair] * 2, mode="lines",
                        line=dict(color=k.LINE, width=3), showlegend=False, hoverinfo="skip")
    fig.add_scatter(x=c.rho_pairwise, y=c.pair, mode="markers", name="complete pairs only",
                    marker=dict(color=k.BLUE, size=12), customdata=c.n_pairwise,
                    hovertemplate="%{y}: ρ %{x:.2f} (n = %{customdata})<extra></extra>")
    fig.add_scatter(x=c.rho_imputed, y=c.pair, mode="markers", name="after income-group imputation",
                    marker=dict(color="#ff9f0a", size=12, symbol="diamond"),
                    hovertemplate="%{y}: ρ %{x:.2f} (n = 214)<extra></extra>")
    fig.update_xaxes(range=[-1, 1], title="Spearman ρ")
    chart(fig.update_layout(title="Same correlation, two ways of handling gaps"), 380, target=a)
    fig = go.Figure(go.Bar(x=[214, att["listwise_n_15cluster"], att["listwise_n_all32"]],
                           y=["all countries", "complete on 15<br>clustering indicators", "complete on<br>all 32"],
                           orientation="h", marker_color=[k.GREY, k.C["soft"], "#ff9f0a"],
                           text=[214, att["listwise_n_15cluster"], att["listwise_n_all32"]], textposition="inside"))
    fig.update_yaxes(autorange="reversed")
    chart(fig.update_layout(title="Countries left under listwise deletion"), 380, legend=False, target=b)

    bridge("These findings decide the preprocessing: skew → log, different scales → standardise, "
           "gaps that are not random → a rule per method.")


# B · preprocessing
FINDINGS = pd.DataFrame([
    ("A1", "1,344 sparse indicators, 5.66 M rows, 574 MB", "B4", "attribute selection (32) + chunked filtering"),
    ("A1", "33 aggregates mixed with countries", "B1", "remove aggregates (empty Region)"),
    ("A1", "metadata in separate files", "B2", "join Country.csv and Series.csv on their keys"),
    ("A1", "long table: one row per value", "B3", "reshape long → wide panel and snapshot"),
    ("A2", "45 % of cells missing, not at random", "B1", "interpolate ≤ 3 years · 10-year snapshot · coverage "
     "threshold · impute only where a method needs it"),
    ("A2", "right skew (skew 1.2–8.9), mean ≫ median", "B3", "log₁₀ transform"),
    ("A2", "scales differ by orders of magnitude", "B3", "z-score standardisation"),
    ("A3", "extreme but genuine values, hyperinflation", "B1", "keep, flag hyperinflation, robust statistics"),
    ("A3", "one correlated block of indicators", "B4", "PCA (one development axis)"),
    ("A3", "near-definitional pairs (infant mortality ↔ life expectancy)", "B5", "drop leaking features per target"),
], columns=["found in", "problem", "group", "technique applied"])


def page_b():
    r = _b_results()
    hero("B · Data preprocessing", "From 5.66 million raw rows<br>to two analysis-ready tables.",
         "Each technique answers a problem found in A. We use all four groups, cleaning (B1), integration (B2), "
         "transformation (B3) and reduction (B4), plus leakage control for the models.")

    section("Which techniques, and why", "Problem found during exploration → preprocessing technique applied.")
    table(FINDINGS.style.hide(axis="index"))
    st.write("")
    stages = pd.DataFrame({"stage": ["raw Indicators.csv", "32 selected indicators", "countries only (no aggregates)",
                                     "panel cells (country-year × 32)", "snapshot cells (country × 32)"],
                           "rows": [5_656_458, 247_446, 210_443, len(panel) * 32, len(snap) * 32]})
    takeaway("The pipeline keeps <em>4 %</em> of the raw rows and loses no country",
             "Values handled at each stage (log scale). Raw-file counts are from the notebook ETL log; the last two "
             "are recomputed from the processed tables.")
    fig = go.Figure(go.Bar(x=stages.rows, y=stages.stage, orientation="h", marker_color=k.BLUE,
                           text=[f"{v:,}" for v in stages.rows], textposition="inside", insidetextanchor="end",
                           textfont=dict(color="#fff")))
    fig.update_xaxes(type="log", title="values (log scale)")
    fig.update_yaxes(autorange="reversed")
    chart(fig, 300, legend=False)
    method_box("Order in which the steps run in `WDI_Analysis.ipynb` and what each changed.", "Full pipeline log",
               ex.PIPELINE.style.hide(axis="index"))

    # B1
    section("B1 · Data cleaning", "Validation, outliers and a missing-value rule for each kind of gap.")
    v = r["valid"]
    st.markdown("**Validation of the processed panel** (recomputed on every load)")
    table(v.style.hide(axis="index"))
    st.markdown("**Missing-value strategy:** one rule per kind of gap")
    table(pd.DataFrame([
        ("1", "linear interpolation of internal gaps ≤ 3 years, never extrapolate", "44.9 → 42.1 % missing"),
        ("2", "snapshot: latest value in 2005–2014", "one value per country"),
        ("3", "impute only where a method needs complete rows", "models: fold median · clusters: group median"),
        ("4", "coverage threshold", "exploration ≥ 60 %, models ≥ 50 %"),
        ("5", "group trends only where ≥ 30 % of the group reports", "no trend from a few countries"),
    ], columns=["#", "rule", "effect"]).style.hide(axis="index"))
    sz = r["sizes"]
    cov = r["cov"]
    listwise = int(sz.set_index("sample").at["listwise: all 32 indicators", "countries"])
    takeaway(f"Our rules keep <em>185–204</em> countries per analysis; deleting incomplete rows would keep "
             f"<em>{listwise}</em>",
             "Left: snapshot coverage per indicator and the two thresholds. Right: countries kept by each rule.")
    a, b = st.columns(2)
    fig = go.Figure(go.Bar(x=cov["coverage_%"], y=[_short(i) for i in cov.indicator], orientation="h",
                           marker_color=[k.BLUE if c >= 60 else ("#ff9f0a" if c >= 50 else "#ff453a")
                                         for c in cov["coverage_%"]],
                           hovertemplate="%{y}: %{x:.0f} % of countries<extra></extra>"))
    for x_, name in ((60, "exploration 60 %"), (50, "models 50 %")):
        fig.add_vline(x=x_, line=dict(color=k.INK, dash="dot"), annotation_text=name, annotation_font_color=k.GREY)
    fig.update_xaxes(range=[0, 101], title="% of countries reporting (snapshot)")
    chart(fig.update_layout(title="Coverage threshold"), 640, legend=False, target=a)
    s2 = sz.iloc[::-1]
    fig = go.Figure(go.Bar(x=s2.countries, y=s2["sample"], orientation="h", text=s2.countries,
                           textposition="inside", textfont=dict(color="#fff"),
                           marker_color=["#ff9f0a" if s.startswith("listwise") else (k.GREY if s.startswith("all")
                                         else k.BLUE) for s in s2["sample"]], customdata=s2.rule,
                           hovertemplate="%{y}: %{x} countries<br>%{customdata}<extra></extra>"))
    fig.update_xaxes(range=[0, 220], title="countries kept")
    chart(fig.update_layout(title="Listwise deletion (orange) vs our rules (blue)"), 640, legend=False, target=b)

    # B2
    section("B2 · Data integration", "Three files joined on their keys into one table per analysis.")
    a, b = st.columns(2)
    with a:
        st.write("")
        table(pd.DataFrame([
            ("Indicators.CountryCode", "Country.CountryCode", "ShortName, Region, IncomeGroup"),
            ("Indicators.IndicatorCode", "Series.SeriesCode", "indicator name, topic, unit"),
            ("IndicatorCode", "alias table (32 rows)", "short name (life_exp) + theme"),
            ("IncomeGroup", "High: OECD + non-OECD", "one 'High income' level → 4 ordinal levels"),
        ], columns=["key", "joined to", "adds"]).style.hide(axis="index"))
    with b:
        ic = snap.groupby(["Region", "Income"], observed=True).size().reset_index(name="countries")
        fig = px.bar(ic, x="countries", y="Region", color="Income", orientation="h",
                     category_orders={"Income": INCOME_ORDER}, color_discrete_map=k.INCOME_COLORS,
                     title="Integrated attributes: region × income group (214 countries)", labels={"Region": ""})
        chart(fig, 330, target=b)
    show = ["CountryCode", "ShortName", "Region", "Income", "gdp_pc", "life_exp", "internet", "co2_pc"]
    st.markdown("**Result: one row per country with metadata and indicators** (snapshot excerpt)")
    table(snap.set_index("CountryCode").loc[[VN, "CHN", "THA", "NGA", "DEU"]].reset_index()[show].style
          .format({"gdp_pc": "{:,.0f}", "life_exp": "{:.1f}", "internet": "{:.1f}", "co2_pc": "{:.2f}"})
          .hide(axis="index"))

    # B3
    section("B3 · Data transformation", "Reshape, log transform and standardise.")
    st.markdown("**Long → wide.** The raw table has one row per value; analysis needs one row per country-year.")
    long = panel[(panel.CountryCode == VN) & panel.Year.between(2010, 2012)][["CountryCode", "Year", "gdp_pc",
                                                                              "life_exp", "internet"]]
    lg = long.melt(["CountryCode", "Year"], var_name="IndicatorCode", value_name="Value")
    a, b = st.columns(2)
    with a:
        st.caption(f"Long (raw format): {len(lg)} rows for 3 years × 3 indicators")
        table(lg.style.format({"Value": "{:,.2f}"}).hide(axis="index"))
    with b:
        st.caption(f"Wide (panel): {len(long)} rows, one column per indicator")
        table(long.style.format({"gdp_pc": "{:,.0f}", "life_exp": "{:.1f}", "internet": "{:.1f}"}).hide(axis="index"))

    sk = r["skew"]
    g = sk.set_index("indicator").loc["gdp_pc"]
    takeaway(f"log₁₀ turns GDP per head from skew <em>{g.skew_raw:.1f}</em> into <em>{g.skew_log10:+.2f}</em>",
             "and makes the income relationships close to linear (the Preston curve in Part 2).")
    a, b = st.columns(2)
    v = a.selectbox("Attribute", sk.indicator.tolist(), format_func=lambda c: LABELS[c], key="b3_var")
    x = snap[v].dropna()
    fig = make_subplots(1, 2, subplot_titles=(f"raw · skew {x.skew():.1f}", f"log₁₀ · skew {np.log10(x.clip(lower=1e-3)).skew():+.2f}"))
    fig.add_histogram(x=x, nbinsx=35, marker_color=k.GREY, row=1, col=1, showlegend=False)
    fig.add_histogram(x=np.log10(x.clip(lower=1e-3)), nbinsx=35, marker_color=k.BLUE, row=1, col=2, showlegend=False)
    chart(fig.update_layout(title=LABELS[v]), 340, legend=False, target=a)
    t = sk.set_index(sk.indicator.map(_short)).drop(columns="indicator")
    t.index.name = None
    with b:
        st.write("")
        table(t.style.format("{:.2f}"))

    d, X, Z = cluster_matrix(snap.assign(Income=snap.Income.astype(str)))
    takeaway("Standardising puts every indicator on the same scale before PCA, clustering and linear models",
             "Clustering inputs after log₁₀ (left) and after z-scores (right): mean 0, standard deviation 1.")
    a, b = st.columns(2)
    raw = X.melt(var_name="indicator", value_name="value")
    fig = px.box(raw, x="indicator", y="value", title="After log₁₀, before standardisation", labels={"indicator": ""})
    fig.update_traces(marker_color=k.GREY, line_color=k.GREY)
    chart(fig, 380, legend=False, target=a)
    zz = pd.DataFrame(Z, columns=X.columns).melt(var_name="indicator", value_name="z")
    fig = px.box(zz, x="indicator", y="z", title="After z-score standardisation", labels={"indicator": ""})
    fig.update_traces(marker_color=k.BLUE, line_color=k.BLUE)
    chart(fig, 380, legend=False, target=b)
    method_box("**Log₁₀** (models): GDP per head (market and PPP), CO₂, energy, trade, and inflation as signed "
               "log₁₀(1 + |x|). **Log₁₀** (clustering): " + ", ".join(CLUSTER_LOG) + ".\n\n"
               "**Standardisation** is fitted inside each cross-validation fold for the models, so test countries "
               "never shape the scaling.\n\n**Derived attributes:** growth rates for convergence (Part 1), country "
               "and year means for fixed effects, and out-of-fold residuals as \"performance vs income\" (Part 2).",
               "Transformation details")

    # B4
    section("B4 · Data reduction", "Fewer attributes, fewer instances, fewer dimensions, with the information kept.")
    pv, pl = r["pca_var"], r["pca_load"]
    takeaway(f"One component keeps <em>{pv['explained_%'].iloc[0]:.1f} %</em> of the information in 15 indicators",
             "PCA on the standardised clustering indicators. PC1 loads almost equally on income, health, schooling, "
             "internet and CO₂, so it is an overall development axis; PC2 is mostly forest cover.")
    a, b, c = st.columns(3)
    fun = pd.DataFrame({"set": ["raw indicators", "selected", "exploration (≥ 60 %)", "clustering", "social (twins)"],
                        "n": [1344, 32, 31, len(CLUSTER_VARS), 10]})
    fig = go.Figure(go.Bar(x=fun.n, y=fun.set, orientation="h", text=fun.n, textposition="outside",
                           marker_color=[k.GREY, k.BLUE, k.BLUE, k.C["soft"], k.C["soft"]]))
    fig.update_xaxes(type="log", range=[0.5, 3.6], title="attributes (log)")
    fig.update_yaxes(autorange="reversed")
    chart(fig.update_layout(title="Attribute selection"), 360, legend=False, target=a)
    fig = go.Figure(go.Bar(x=pv.component, y=pv["explained_%"], marker_color=k.BLUE, name="explained"))
    fig.add_scatter(x=pv.component, y=pv["cumulative_%"], mode="lines+markers", name="cumulative",
                    line=dict(color="#ff9f0a", width=2.5))
    fig.update_yaxes(range=[0, 101], title="% of variance")
    chart(fig.update_layout(title="PCA scree"), 360, target=b)
    pl = pl.sort_values("PC1")
    fig = go.Figure(go.Bar(x=pl.PC1, y=[_short(i) for i in pl.indicator], orientation="h",
                           marker_color=[k.BLUE if v > 0 else "#ff9f0a" for v in pl.PC1]))
    fig.update_xaxes(title="PC1 loading")
    chart(fig.update_layout(title="What PC1 measures"), 360, legend=False, target=c)
    st.markdown(f"**Instance reduction:** 55 years × 214 countries ({len(panel):,} country-years) → one snapshot row "
                f"per country ({len(snap)}), for every cross-country comparison; the panel is kept for trends and "
                "fixed effects.")

    # B5
    section("B5 · Leakage control for the models", "Near-definitional features are removed per target, and "
            "cross-validation folds are split by country.")
    table(pd.DataFrame([(t, LABELS[s["target"]], ", ".join(LABELS[f] for f in s["leak"]))
                        for t, s in THEMES.items()], columns=["theme", "target", "features dropped"])
          .style.hide(axis="index"))

    bridge("With clean, comparable tables we can tell the story: how did the world change?")

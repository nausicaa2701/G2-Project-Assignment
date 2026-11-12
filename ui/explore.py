"""Lab: free-exploration tabs (countries, model lab, clusters)."""
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score

from ui import core as k
from ui.core import (INCOME_ORDER, LABELS, LOG_SCALE, THEME_VARS, load_results, panel, section,
                     snap, style, table, tiles)
from wdi.models import MODEL_NAMES, THEMES, Config, evaluate, summarise
from wdi.story.part3 import CLUSTER_VARS, cluster_matrix, fit_clusters


def page_countries():
    section("Countries", "Pick one indicator: the map, the ranking and the country lines all follow it.")
    c1, c2 = st.columns([1, 2])
    theme = c1.selectbox("Theme", list(THEME_VARS), index=list(THEME_VARS).index("Health"))
    var = c2.selectbox("Indicator", THEME_VARS[theme], format_func=LABELS.get)

    d = snap.dropna(subset=[var])
    color = np.log10(d[var].clip(lower=1e-3)) if var in LOG_SCALE else d[var]
    fig = go.Figure(go.Choropleth(locations=d.CountryCode, z=color, text=d.ShortName, colorscale="Blues",
                                  customdata=d[var], hovertemplate="%{text}<br>%{customdata:,.2f}<extra></extra>",
                                  marker_line_color=k.C["card"], marker_line_width=0.4,
                                  colorbar=dict(title="log₁₀" if var in LOG_SCALE else "", thickness=10)))
    fig.update_geos(showframe=False, showcoastlines=False, projection_type="natural earth",
                    projection_rotation_lon=0, lonaxis_range=[-180, 180], lataxis_range=[-58, 85])
    st.plotly_chart(style(fig, 460, legend=False).update_layout(title=f"{LABELS[var]} · latest value 2005–2014"),
                    width="stretch", theme=None)

    names = sorted(panel.ShortName.dropna().unique())
    pick = st.multiselect("Countries over time", names, default=["Vietnam", "China", "Thailand", "Indonesia", "India"])
    p = panel[panel.ShortName.isin(pick)].dropna(subset=[var])
    fig = px.line(p, x="Year", y=var, color="ShortName", log_y=var in LOG_SCALE, labels={var: "", "ShortName": ""},
                  title=LABELS[var])
    fig.update_traces(line_width=2.5)
    st.plotly_chart(style(fig, 420), width="stretch", theme=None)

    n = st.slider("Lowest and highest", 5, 20, 10)
    s = d.sort_values(var)
    a, b = st.columns(2)
    for col, part, title in ((a, s.head(n), "Lowest"), (b, s.tail(n), "Highest")):
        fig = px.bar(part, x=var, y="ShortName", orientation="h", color="Income", color_discrete_map=k.INCOME_COLORS,
                     category_orders={"Income": INCOME_ORDER}, labels={var: "", "ShortName": ""}, title=f"{title} {n}")
        col.plotly_chart(style(fig, 120 + 28 * n), width="stretch", theme=None)

    section("Relationship explorer", "Any two indicators, one bubble per country (size = population).")
    c1, c2 = st.columns(2)
    keys = list(LABELS)
    x = c1.selectbox("X axis", keys, index=keys.index("gdp_pc"), format_func=LABELS.get)
    y = c2.selectbox("Y axis", keys, index=keys.index(var if var != x else "life_exp"), format_func=LABELS.get)
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
        st.info("No precomputed results yet. Run section 9 of WDI_Analysis.ipynb or use the live lab below.")
    else:
        targets = {t: LABELS[v["target"]] + (" (log)" if v["log"] else "") for t, v in THEMES.items()}
        best = summary.sort_values("r2_mean", ascending=False).groupby("theme").head(1).set_index("theme")
        tiles([(t, f"{best.loc[t, 'r2_mean']:.2f}", f"{best.loc[t, 'model']} · {targets[t]}")
               for t in THEMES if t in best.index])
        st.write("")
        theme = st.selectbox("Theme", list(THEMES), format_func=lambda t: f"{t}: {targets[t]}")
        s = summary[summary.theme == theme].sort_values("r2_mean")
        fig = go.Figure(go.Bar(x=s.r2_mean, y=s.model, orientation="h", error_x=dict(array=s.r2_std, color=k.GREY),
                               marker_color=[k.BLUE if m == s.model.iloc[-1] else k.C["soft"] for m in s.model],
                               hovertemplate="%{y}: R² %{x:.3f}<extra></extra>"))
        fig.update_xaxes(range=[max(0, s.r2_mean.min() - 0.1), 1])
        a, b = st.columns(2)
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
                fig.add_scatter(x=g.Year, y=g.actual, name=inc, line=dict(color=k.INCOME_COLORS[inc], width=3))
                fig.add_scatter(x=g.Year, y=g.pred, name=f"{inc} · models", showlegend=False,
                                line=dict(color=k.INCOME_COLORS[inc], width=2, dash="dot"))
            fig.update_layout(title="Actual (solid) vs mean of all models (dotted)")
            if THEMES[theme]["log"]:
                fig.update_yaxes(type="log")
            a.plotly_chart(style(fig, 440), width="stretch", theme=None)
        if imp is not None:
            i = imp[imp.theme == theme].head(12).iloc[::-1]
            fig = px.bar(i, x="importance", y=i.feature.map(lambda f: LABELS.get(f, f)), orientation="h",
                         error_x="std", title=f"What drives it? Permutation importance ({i.model.iloc[0]})",
                         labels={"y": "", "importance": "drop in R² when shuffled"})
            fig.update_traces(marker_color=k.BLUE)
            b.plotly_chart(style(fig, 440, legend=False), width="stretch", theme=None)

    section("Leakage control", "Near-definitional features are removed per target, and cross-validation folds "
            "are split by country, so no country is in both train and test.")
    table(pd.DataFrame([(t, LABELS[s["target"]], ", ".join(LABELS[f] for f in s["leak"]))
                        for t, s in THEMES.items()], columns=["theme", "target", "features dropped"])
          .style.hide(axis="index"))

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
    n_k = c2.slider("Clusters (k)", 2, 8, 4)
    seed = c3.number_input("Seed", 0, 10_000, 42)
    d, X, Z = cluster_matrix(snap)
    lab = fit_clusters(Z, X.gdp_pc, algo, n_k, seed)
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
                     color_discrete_sequence=k.CLUSTER_COLORS)
    fig.update_traces(marker=dict(size=9, line=dict(width=0.5, color=k.C["card"])))
    a.plotly_chart(style(fig, 460), width="stretch", theme=None)
    fig = px.choropleth(d, locations="CountryCode", color="Cluster", hover_name="ShortName",
                        category_orders={"Cluster": cats}, title="Where the clusters are",
                        color_discrete_sequence=k.CLUSTER_COLORS)
    fig.update_geos(showframe=False, showcoastlines=False, projection_type="natural earth", projection_rotation_lon=0,
                    lonaxis_range=[-180, 180], lataxis_range=[-58, 85])
    b.plotly_chart(style(fig, 460), width="stretch", theme=None)
    prof = snap.set_index("CountryCode").loc[d.CountryCode, vars_].groupby(d.Cluster.values).median().T
    prof.index = prof.index.map(LABELS)
    table(prof.style.format("{:,.1f}").background_gradient(cmap="Blues", axis=1))


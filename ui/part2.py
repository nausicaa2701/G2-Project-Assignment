"""Part 2 · WHY: "Income explains most of development; the residual is the story."

Reads results/story/part2/ (python run_story.py --part 2).
"""
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from ui import core as k
from ui.core import (LABELS, NAMES, VN, bridge, country_picker, hero, highlight_colors, load_results,
                     method_box, snap, style, table, takeaway)
from wdi.models import THEMES
from wdi.story.part2 import PEERS, layer_table

P2_LABEL = {"Health": "Health · life expectancy", "Technology": "Technology · internet users",
            "Demography": "Demography · fertility", "Education": "Education · secondary enrolment",
            "Environment": "Environment · CO₂ per head"}


def _p2_income_scatter(theme, fit, codes, title, h=480):
    """One dot per country, the income-only line (Preston / EKC style), highlighted countries on top."""
    t = THEMES[theme]["target"]
    f = fit.set_index("theme").loc[theme]
    d = snap.dropna(subset=[t, "gdp_pc"])
    fig = go.Figure(go.Scatter(x=d.gdp_pc, y=d[t], mode="markers", text=d.ShortName, name="Other countries",
                               marker=dict(color=k.GREY, size=7, opacity=.35),
                               hovertemplate="%{text}<br>GDP %{x:$,.0f}<br>%{y:,.1f}<extra></extra>"))
    xs = np.logspace(np.log10(d.gdp_pc.min()), np.log10(d.gdp_pc.max()), 60)
    ys = f.intercept + f.slope_per_10x * np.log10(xs)
    fig.add_scatter(x=xs, y=10 ** ys if f.log_target else ys, mode="lines", name="What income predicts",
                    line=dict(color=k.INK, width=2, dash="dot"), hoverinfo="skip")
    hl = d.set_index("CountryCode").reindex(codes).dropna(subset=[t])
    for c, r in hl.iterrows():
        fig.add_scatter(x=[r.gdp_pc], y=[r[t]], mode="markers+text", text=[r.ShortName], textposition="top center",
                        name=r.ShortName, marker=dict(color=highlight_colors(codes)[c], size=15 if c == VN else 11,
                                                      line=dict(color=k.C["card"], width=1.5)),
                        textfont=dict(color=highlight_colors(codes)[c], size=13 if c == VN else 11))
    fig.update_xaxes(type="log", title="GDP per capita, const. 2005 US$ (log scale)")
    fig.update_yaxes(type="log" if f.log_target else "linear", title=LABELS[t])
    return style(fig.update_layout(title=title), h)


def page():
    layers = load_results("story/part2/E2_1_r2_layers.csv")
    res = load_results("story/part2/E2_2_residuals.csv")
    fit = load_results("story/part2/E2_2_income_fit.csv")
    fe = load_results("story/part2/E2_3_fixed_effects.csv")
    yfx = load_results("story/part2/E2_3_year_effects.csv")
    if any(x is None for x in (layers, res, fit, fe, yfx)):
        st.warning("Precomputed results are missing. Run section 10 of WDI_Analysis.ipynb first.")
        return
    health = fit.set_index("theme").loc["Health"]
    vn = res[res.CountryCode == VN].set_index("theme")

    hero("Part 2 · Why", "Ten times richer, about ten years longer.<br>But that is not the whole story.",
         "Income explains most of the differences between countries. The countries that beat their income "
         "are where the interesting lessons are.")
    codes = country_picker("p2_pick", PEERS)

    # 1 · almost everything moves with income (folded under the Preston curve)
    num = [c for c in LABELS if c in snap and c not in ("gdp_pc", "gdp_pc_ppp", "population")]
    rho = snap[num].corrwith(snap.gdp_pc, method="spearman").dropna().sort_values(key=abs)
    strong = int((rho.abs() >= .5).sum())

    # 2 · the Preston curve
    takeaway(f"Each 10× more income goes with <em>+{health.slope_per_10x:.0f} years</em> of life",
             f"Income alone explains R² = {health.r2:.2f} of life expectancy across {health.n:.0f} countries. "
             "The dotted line is what income predicts; distance from it is the residual.")
    st.plotly_chart(_p2_income_scatter("Health", fit, codes, "Life expectancy vs income (the Preston curve)"),
                    width="stretch", theme=None)
    with st.expander(f"Not only health: {strong} of {len(rho)} indicators move closely with income"):
        st.markdown("Spearman correlation with GDP per capita across countries (latest value 2005–2014). "
                    "|ρ| ≥ 0.5 counts as close.")
        fig = go.Figure(go.Bar(x=rho.values, y=[LABELS[i] for i in rho.index], orientation="h",
                               marker_color=[k.BLUE if v > 0 else "#ff9f0a" for v in rho.values],
                               text=[f"{v:+.2f}" for v in rho.values], textposition="outside",
                               hovertemplate="%{y}: ρ = %{x:.2f}<extra></extra>"))
        fig.update_xaxes(range=[-1.1, 1.1], title="ρ with GDP per capita (blue: rises with income, orange: falls)")
        st.plotly_chart(style(fig, 140 + 22 * len(rho), legend=False), width="stretch", theme=None)

    # 3 · E2.1 R² in three layers
    lt = layer_table(layers)
    lt["label"] = lt.theme.map(P2_LABEL)
    share, r2_inc = lt.income_share.mean(), lt.income.mean()
    takeaway(f"Income alone explains R² <em>{r2_inc:.2f}</em>, already <em>{share:.0%}</em> of what the best "
             "model reaches",
             "Cross-validated R² per theme, built up in three layers. More indicators help; the 19-model zoo adds "
             f"only {lt.add_complexity.min():.2f}–{lt.add_complexity.max():.2f} on top.")
    fig = go.Figure()
    for col, name, color in (("income", "Income alone (log GDP, Ridge)", k.BLUE),
                             ("add_features", "+ all other indicators (Ridge)", k.C["soft"]),
                             ("add_complexity", "+ best of 19 models", k.GREY)):
        fig.add_bar(y=lt.label, x=lt[col], orientation="h", name=name, marker_color=color,
                    text=[f"{v:.2f}" if v >= .04 else "" for v in lt[col]], textposition="inside", textangle=0,
                    hovertemplate="%{y}<br>" + name + ": %{x:.3f}<extra></extra>")
    fig.update_layout(barmode="stack", legend_traceorder="normal")
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(range=[0, 1], title="cross-validated R²")
    st.plotly_chart(style(fig, 380), width="stretch", theme=None)
    tbl = lt.set_index("label")[["income", "all", "best", "best_model", "income_share"]]
    tbl.columns = ["Income only", "All indicators", "Best model R²", "Best model", "Income share"]
    tbl.index.name = None
    method_box(
        "**Target per theme:** life expectancy, internet users, fertility, secondary enrolment, CO₂ per head (log). "
        "Economy is left out because its target is income itself.\n\n"
        "**Preprocessing** (same as `wdi/models.py`): latest value per country in 2005–2014 · log₁₀ for skewed "
        "variables (GDP, CO₂, energy, inflation, trade) · indicators that nearly define the target are dropped "
        "(e.g. infant and under-5 mortality when predicting life expectancy) · features observed for < 50 % of "
        "countries are dropped · missing values are filled with the median inside each training fold · "
        "standardised. The income-only model uses only countries with an observed GDP.\n\n"
        "**Evaluation:** grouped 5-fold cross-validation by country, so no country is in both train and test, "
        "repeated over 5 seeds (std of R² ≤ 0.02). Layer 3 is the best of 19 models in "
        "`results/summary_snapshot.csv` (Linear, Ridge, Lasso, ElasticNet, BayesianRidge, Huber, KNN, SVR, "
        "DecisionTree, RandomForest, ExtraTrees, GradientBoosting, HistGB, AdaBoost, MLP, XGBoost, LightGBM, "
        "Voting, Stacking).",
        styler=tbl.style.format({"Income only": "{:.2f}", "All indicators": "{:.2f}", "Best model R²": "{:.2f}",
                                 "Income share": "{:.0%}"}))

    # 4 · E2.2 residual scorecard
    h = vn.loc["Health"]
    takeaway(f"Vietnam lives <em>{h.gap:+.1f} years</em> longer than its income predicts: "
             f"#{h['rank']} of {h.n}",
             "Each dot is a country's percentile against what its income predicts (100 = beats its income the most). "
             "For fertility and CO₂, lower than predicted counts as better.")
    order = ["Health", "Technology", "Demography", "Education", "Environment"]
    pos = {t: i for i, t in enumerate(order)}
    rng = np.random.default_rng(0)
    fig = go.Figure(go.Scatter(x=res.score, y=res.theme.map(pos) + rng.uniform(-.22, .22, len(res)),
                               mode="markers", text=res.ShortName, name="All countries",
                               marker=dict(color=k.GREY, size=6, opacity=.25),
                               hovertemplate="%{text}: %{x:.0f}th percentile<extra></extra>"))
    sel = res[res.CountryCode.isin(codes)]
    colors = highlight_colors(codes)
    for c in codes:
        r = sel[sel.CountryCode == c]
        if r.empty:
            continue
        fig.add_scatter(x=r.score, y=r.theme.map(pos), mode="markers", name=NAMES[c],
                        marker=dict(color=colors[c], size=17 if c == VN else 12, line=dict(color=k.C["card"], width=1.5),
                                    symbol="circle" if c == VN else "diamond"),
                        customdata=np.c_[r.gap, r["rank"], r.n],
                        hovertemplate=NAMES[c] + ": %{x:.0f}th percentile, rank %{customdata[1]:.0f}/%{customdata[2]:.0f}"
                                      "<extra></extra>")
    fig.add_vline(x=50, line=dict(color=k.LINE, dash="dot"))
    fig.update_yaxes(tickvals=list(pos.values()), ticktext=[P2_LABEL[t] for t in order], autorange="reversed",
                     showgrid=False)
    fig.update_xaxes(range=[-2, 103], title="← worse than income predicts · percentile · better than income predicts →")
    st.plotly_chart(style(fig, 420), width="stretch", theme=None)

    def fmt(r):
        if pd.isna(r.gap):
            return "–"
        g = f"{r.gap:.1f}×" if r.theme == "Environment" else f"{r.gap:+.1f}"
        return f"{g}  (#{r['rank']}/{r.n})"
    card = sel.assign(cell=sel.apply(fmt, axis=1), Country=sel.CountryCode.map(NAMES)).pivot(
        index="Country", columns="theme", values="cell").reindex(columns=order).fillna("–")
    card = card.reindex([NAMES[c] for c in codes if NAMES[c] in card.index])
    card.columns = [f"{P2_LABEL[t].split(' · ')[1]} ({UNIT})" for t, UNIT in
                    zip(order, ["years", "per 100", "births", "pp", "× predicted"])]
    card.index.name = None
    table(card.style)
    method_box(
        "**Residual** = actual value minus the value predicted from log GDP alone. Predictions are out-of-fold "
        "(the country was not used to fit its own prediction) and averaged over 5 seeds. "
        "CO₂ is modelled in log₁₀, so its residual is a ratio (3× = three times what income predicts). "
        "Rank 1 = beats its income by the most. Countries without data for a theme show “–”.",
        "How the scorecard is computed")

    # 5 · E2.3 richer vs getting richer
    fh = fe.set_index("theme").loc["Health"]
    yh = yfx[yfx.theme == "Health"]
    shift = yh.effect.iloc[-1]
    fold = st.expander(f"Richer vs getting richer: +{fh.within:.1f} years per 10× within a country")
    fold.markdown(f"**Getting richer adds only +{fh.within:.1f} years per 10×; time itself added +{shift:.1f}.** "
                  "Between countries, 10× more income goes with ~11 more years. Within one country over time, the "
                  "same rise in income goes with far less, while life expectancy rose for everyone at the same income.")
    a, b = fold.columns(2)
    fig = go.Figure(go.Bar(x=["Between countries<br>(richer)", "Within a country<br>(getting richer)"],
                           y=[fh["between"], fh.within], marker_color=[k.GREY, k.BLUE],
                           error_y=dict(type="data", array=[0, 1.96 * fh.within_se], color=k.INK),
                           text=[f"+{fh['between']:.1f}", f"+{fh.within:.1f}"], textposition="inside",
                           textfont=dict(color="#fff", size=15)))
    fig.update_yaxes(title="years of life expectancy per 10× GDP per capita")
    a.plotly_chart(style(fig.update_layout(title="Income slope, 1990–2014"), 420, legend=False), width="stretch",
                   theme=None)
    fig = px.line(yh, x="Year", y="effect", title="Life expectancy at constant income, vs 1990",
                  labels={"effect": "years", "Year": ""})
    fig.update_traces(line=dict(width=3, color=k.BLUE))
    b.plotly_chart(style(fig, 420, legend=False), width="stretch", theme=None)
    fe_t = fe.set_index(fe.theme.map(P2_LABEL))[["between", "within", "within_lo", "within_hi", "n_countries", "n_obs"]]
    fe_t.columns = ["Between countries", "Within (country + year FE)", "95% CI low", "95% CI high", "Countries",
                    "Country-years"]
    fe_t.index.name = None
    fold.markdown(
        "**Data:** panel 1990–2014, countries with ≥ 5 years of data. Slope = change in the target per 10× GDP per "
        "capita (CO₂ in log₁₀ units, so 0.75 means ×5.6 CO₂ per 10× income).\n\n"
        "**Between:** regression of country averages, the same comparison as the Preston curve. "
        "**Within:** two-way fixed effects (country and year), so only changes inside a country relative to the "
        "global trend count. Standard errors clustered by country. The year effects on the right are the "
        "common shift of all countries at a given income.\n\n"
        "**Reading:** cross-country gaps overstate what income growth alone buys. Medicine, vaccines and public "
        "health spread to everyone over time. This is still an association, not a causal estimate.")
    with fold:
        table(fe_t.style.format({c: "{:.2f}" for c in fe_t.columns[:4]}))

    # 6 · the cost: CO₂
    e = vn.loc["Environment"]
    fenv = fit.set_index("theme").loc["Environment"]
    takeaway(f"The cost: CO₂ rises <em>{10 ** fenv.slope_per_10x:.0f}×</em> for every 10× more income. "
             f"Vietnam emits <em>{e.gap:.1f}×</em> what its income predicts",
             "Even within countries over time, CO₂ tracks income closely. The cross-country turning point of the "
             "Kuznets curve (~US$51,000 per head, notebook §8.4) lies beyond almost every country.")
    st.plotly_chart(_p2_income_scatter("Environment", fit, codes, "CO₂ per head vs income (log–log)"),
                    width="stretch", theme=None)

    bridge("Income does not tell the whole story. So do income groups classify countries correctly?")

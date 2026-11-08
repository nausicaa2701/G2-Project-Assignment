"""Part 1 · WHAT: "The world progressed, but unevenly".

Reads results/story/E1_*.csv (python -m wdi.story E1.1 E1.2 E1.3); the β scatter points are recomputed live.
"""
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from ui import core as k
from ui.core import (INCOME_ORDER, VN, VN_COLOR, bridge, chart, group_trend, hero, load_results, method_box,
                     missing_results, panel, takeaway)
from wdi.story import part1 as p1

SIGMA_LABEL = {"life_exp": "Life expectancy", "enrol_primary": "Primary enrolment", "gdp_pc": "GDP per head",
               "fertility": "Fertility", "u5_mort": "Under-5 mortality", "internet": "Internet users"}


@st.cache_data(show_spinner=False)
def _beta_points():
    return p1.e1_2_beta(p1.panel())[1]


def _p90_p10(year):
    g = panel.loc[panel.Year == year, "gdp_pc"].dropna()
    return g.quantile(.9) / g.quantile(.1), len(g)


def page():
    sigma, beta, robust = (load_results(f"story/{n}.csv") for n in ("E1_1_sigma", "E1_2_beta", "E1_3_robustness"))
    if missing_results(sigma, beta, robust, cmd="python -m wdi.story E1.1 E1.2 E1.3"):
        return

    le = group_trend("life_exp", "Income").pivot(index="Year", columns="Income", values="median")
    gap = (le["High income"] - le["Low income"]).dropna()
    r0, n0 = _p90_p10(1990)
    r1, n1 = _p90_p10(2013)
    hero("Part 1 · What", "The world progressed,<br>but unevenly.",
         "Does richer mean more developed? First, what actually happened between 1960 and 2014: "
         "who caught up, on what, and who did not.")

    # 1.1 · the paradox
    takeaway(f"The life-expectancy gap shrank from <em>{gap.iloc[0]:.0f}</em> to <em>{gap.iloc[-1]:.0f} years</em>, "
             f"while the income gap did not move: <em>{r0:.0f}×</em> in 1990, <em>{r1:.0f}×</em> in 2013",
             "Left: median life expectancy by World Bank income group. Right: GDP per head of the richest 10 % of "
             "countries divided by the poorest 10 %.")
    a, b = st.columns(2)
    d = group_trend("life_exp", "Income")
    fig = px.line(d, x="Year", y="median", color="Income", category_orders={"Income": INCOME_ORDER},
                  color_discrete_map=k.INCOME_COLORS, labels={"median": "years", "Year": ""},
                  title="Life expectancy, median by income group")
    fig.update_traces(line_width=3)
    chart(fig, 420, target=a)
    yrs = [y for y in range(1970, 2015) if panel.loc[panel.Year == y, "gdp_pc"].notna().sum() > 100]
    ratio = pd.DataFrame([(y, *_p90_p10(y)) for y in yrs], columns=["Year", "ratio", "n"])
    fig = px.line(ratio, x="Year", y="ratio", labels={"ratio": "p90 / p10", "Year": ""},
                  title="Income gap between countries (p90 / p10)")
    fig.update_traces(line=dict(width=3, color=k.INK))
    chart(fig, 420, legend=False, target=b)

    # 1.2 · can we trust it
    rb = robust.copy()
    held = (rb.groupby("indicator").direction.nunique() == 1).sum()
    takeaway(f"The trends are not an artefact of missing data: the direction holds for <em>{held} of "
             f"{rb.indicator.nunique()}</em> indicators on a balanced panel",
             "About 42 % of panel cells are empty, mostly because some series start in 1990. Re-running the "
             "convergence measure only on countries that report in both years gives the same picture. "
             "Details of the data handling are on pages A and B.")
    rb["CV"] = rb.apply(lambda r: f"{r.cv_start:.2f} → {r.cv_end:.2f}", axis=1)
    t = rb.pivot(index="indicator", columns="version", values="CV")
    t.index = t.index.map(SIGMA_LABEL)
    t.index.name = None
    t.columns.name = None
    dirs = rb.pivot(index="indicator", columns="version", values="direction")
    t["direction (balanced panel)"] = dirs["balanced panel"].rename(index=SIGMA_LABEL)
    method_box("**E1.3 robustness:** coefficient of variation (CV) 1990 → 2013 for (a) every reporting country, "
               "(b) a balanced panel of countries reporting in both years, (c) the balanced panel weighted by "
               "population. A change of more than 5 % counts as converging or diverging. GDP convergence on the "
               "weighted panel is mostly China and India growing.",
               "E1.3 · same result on a balanced panel?",
               t.style)

    # 1.3 · what converges (E1.1)
    s = sigma.sort_values("Year")
    first = s.groupby("indicator").cv.first()
    last = s.groupby("indicator").cv.last()
    takeaway(f"Health and schooling converged; income did not: life-expectancy CV <em>{first['life_exp']:.2f} → "
             f"{last['life_exp']:.2f}</em>, GDP CV <em>{first['gdp_pc']:.2f} → {last['gdp_pc']:.2f}</em>",
             "σ-convergence: the spread between countries (coefficient of variation) each year, relative to the "
             "first year with more than 100 reporting countries. Below 1 means countries became more alike.")
    pick = st.multiselect("Indicators", list(SIGMA_LABEL), default=list(SIGMA_LABEL), format_func=SIGMA_LABEL.get,
                          key="p1_sigma")
    fig = go.Figure()
    for v in pick:
        g = s[s.indicator == v]
        gdp = v == "gdp_pc"
        fig.add_scatter(x=g.Year, y=g.cv / g.cv.iloc[0], mode="lines", name=SIGMA_LABEL[v],
                        line=dict(width=4 if gdp else 2.5, color=k.INK if gdp else None, dash="dash" if gdp else None),
                        customdata=g.cv, hovertemplate=SIGMA_LABEL[v] + " %{x}: CV %{customdata:.2f}<extra></extra>")
    fig.add_hline(y=1, line=dict(color=k.LINE, dash="dot"))
    fig.update_yaxes(title="CV relative to the first year")
    chart(fig.update_layout(title="Spread between countries over time (GDP: dashed)"), 440)

    # 1.4 · the Sub-Saharan exception
    fr = group_trend("fertility", "Region")
    w = fr.pivot(index="Year", columns="Region", values="median")
    chg = 100 * (w.loc[2013] / w.loc[1960] - 1)
    ssa = chg["Sub-Saharan Africa"]
    dev = chg.drop(["Sub-Saharan Africa", "Europe & Central Asia", "North America"], errors="ignore")
    takeaway(f"Except one: fertility fell only <em>{abs(ssa):.0f} %</em> in Sub-Saharan Africa (1960–2013), "
             f"against {abs(dev.max()):.0f}–{abs(dev.min()):.0f} % in the other developing regions",
             "Median births per woman by region. Europe and North America started from low fertility and fell "
             f"{abs(chg.get('Europe & Central Asia', float('nan'))):.0f} % and {abs(chg.get('North America', float('nan'))):.0f} %. "
             "The demographic transition is incomplete in Sub-Saharan Africa, so the spread between countries grew.")
    fig = px.line(fr, x="Year", y="median", color="Region", labels={"median": "births per woman", "Year": ""},
                  title="Fertility, median by region")
    fig.update_traces(line_width=2, opacity=.55)
    fig.update_traces(selector=dict(name="Sub-Saharan Africa"), line=dict(width=4.5, color=VN_COLOR), opacity=1)
    chart(fig, 420)

    # 1.5 · income did not converge (E1.2)
    pts = _beta_points()
    b_ = beta.set_index("indicator")
    gdp = b_.loc["gdp_pc"]
    others = b_.drop("gdp_pc")
    vn_g = gdp.vn_change
    takeaway(f"Poorer countries did not grow faster: income β gives r = <em>{gdp.r:+.2f}</em> (p = {gdp.p:.2f}), "
             f"against r = {others.r.max():+.2f} to {others.r.min():+.2f} for health, schooling and fertility",
             f"β-convergence: change per year since 1990 against the 1990 level; a falling line means catch-up. "
             f"Vietnam (red) grew {vn_g:.1f} % a year, one of the few that broke away.")
    names = {"gdp_pc": "GDP per head (log growth %/yr)", "life_exp": "Life expectancy (years/yr)",
             "enrol_primary": "Primary enrolment (pp/yr)", "fertility": "Fertility (births/yr)"}
    order = list(names)
    fig = make_subplots(1, 4, subplot_titles=[f"{names[v]}<br>r = {b_.at[v, 'r']:+.2f}" for v in order],
                        horizontal_spacing=.06)
    for i, v in enumerate(order, 1):
        g = pts[pts.indicator == v]
        fig.add_scatter(x=g.x, y=g.change, mode="markers", marker=dict(color=k.GREY, size=6, opacity=.45),
                        text=g.CountryCode, hovertemplate="%{text}<extra></extra>", showlegend=False, row=1, col=i)
        xs = np.linspace(g.x.min(), g.x.max(), 2)
        fig.add_scatter(x=xs, y=b_.at[v, "beta"] * xs + (g.change.mean() - b_.at[v, "beta"] * g.x.mean()),
                        mode="lines", line=dict(color=k.INK, width=2), showlegend=False, hoverinfo="skip", row=1, col=i)
        vn = g[g.CountryCode == VN]
        if len(vn):
            fig.add_scatter(x=vn.x, y=vn.change, mode="markers", marker=dict(color=VN_COLOR, size=13),
                            showlegend=False, hovertemplate="Vietnam<extra></extra>", row=1, col=i)
        fig.update_xaxes(title_text="1990 level" + (" (log₁₀)" if v == "gdp_pc" else ""), row=1, col=i)
    fig.update_annotations(font_size=12)
    chart(fig, 380, legend=False)
    bt = b_[["period", "n", "beta", "ci_low", "ci_high", "r", "p", "vn_change"]].copy()
    bt.index = bt.index.map(names)
    bt.index.name = None
    method_box("**β-convergence (E1.2):** OLS of the annual change between 1990 and the last year with more than "
               "100 reporting countries on the 1990 level. GDP uses log growth in % per year on the log₁₀ level; the "
               "others use units per year on the level. β < 0 means catch-up; the 95 % CI comes from the t "
               "distribution.\n\n**σ-convergence (E1.1):** CV = standard deviation / mean across countries, for years "
               "with more than 100 reporting countries.",
               "Method & all coefficients",
               bt.style.format({"n": "{:.0f}", "beta": "{:.3f}", "ci_low": "{:.3f}", "ci_high": "{:.3f}",
                                "r": "{:+.2f}", "p": "{:.3f}", "vn_change": "{:.2f}"}))

    bridge("Health converged while income did not. So how much does income really matter?")

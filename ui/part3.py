"""Part 3 · SO WHAT: "Look with data, not only with income: where does Vietnam stand?"

Reads results/story/E3_*.csv (python -m wdi.story E3.1 E3.2 E3.3); the reference clustering is recomputed live.
"""
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score

from ui import core as k
from ui.core import (INCOME_ORDER, LABELS, VN, VN_COLOR, bridge, chart, hero, insights, load_results, method_box,
                     missing_results, snap, takeaway)
from wdi.story.part3 import CLUSTER_NAMES, cluster_matrix, fit_clusters, income_agreement

NAME_ORDER = list(CLUSTER_NAMES.values())


@st.cache_data(show_spinner=False)
def _reference():
    """K-means, k = 4, seed 42 (the reference of E3.1) with PCA coordinates."""
    d, X, Z = cluster_matrix(snap.assign(Income=snap.Income.astype(str)))
    lab = fit_clusters(Z, X.gdp_pc)
    pca = PCA(2).fit(Z)
    P = pca.transform(Z)
    if np.corrcoef(P[:, 0], X.gdp_pc)[0, 1] < 0:
        P[:, 0] *= -1
    d = d.assign(cluster=pd.Series(lab).map(CLUSTER_NAMES), PC1=P[:, 0], PC2=P[:, 1])
    return d, pca.explained_variance_ratio_, silhouette_score(Z, lab), income_agreement(lab, d.Income)


def page():
    rob, twins, gaps = (load_results(f"story/{n}.csv") for n in ("E3_1_cluster_robustness", "E3_2_twins", "E3_3_gaps"))
    if missing_results(rob, twins, gaps, cmd="python -m wdi.story E3.1 E3.2 E3.3"):
        return
    d, ev, sil, agree = _reference()
    hero("Part 3 · So what", "Look with data,<br>not only with income.",
         "If income does not tell the whole story, are income groups the right way to compare countries? "
         "And where does Vietnam really stand?")

    # 3.2 · clusters vs income groups
    r = rob.set_index("algorithm")
    km = r.loc["K-means"]
    takeaway(f"Four data-driven clusters match income groups for <em>{agree:.0%}</em> of countries; "
             "the mismatches are the interesting part",
             f"K-means (k = 4) is stable: ARI {km.ari_between_seeds:.2f} between seeds, but the silhouette is only "
             f"{sil:.2f}: development is one continuous axis (PC1 = {ev[0]:.0%} of the variance, Data A3), so any "
             "grouping cuts a continuum.")
    a, b = st.columns(2)
    ct = pd.crosstab(pd.Categorical(d.cluster, NAME_ORDER), pd.Categorical(d.Income, INCOME_ORDER))
    fig = px.imshow(ct.values, x=["Low", "Lower-mid", "Upper-mid", "High"], y=NAME_ORDER, text_auto=True,
                    color_continuous_scale="Blues", aspect="auto", labels=dict(x="income group", y="", color="countries"),
                    title="Cluster × income group (countries)")
    chart(fig, 380, legend=False, target=a)
    rr = rob.melt("algorithm", ["ari_between_seeds", "agreement", "vn_emerging_share"], "metric", "value")
    rr["metric"] = rr.metric.map({"ari_between_seeds": "ARI between seeds", "agreement": "agreement with income groups",
                                  "vn_emerging_share": "Vietnam in 'Emerging'"})
    fig = px.bar(rr, x="algorithm", y="value", color="metric", barmode="group", labels={"algorithm": "", "value": ""},
                 color_discrete_sequence=[k.BLUE, k.C["soft"], VN_COLOR], title="E3.1 · robustness over 20 seeds")
    fig.update_yaxes(range=[0, 1.05], tickformat=".0%")
    chart(fig, 380, target=b)
    rank = {g: i for i, g in enumerate(INCOME_ORDER)}
    cl_rank = {g: i for i, g in enumerate(NAME_ORDER)}
    mism = d[(d.cluster.map(cl_rank) - d.Income.map(rank)).abs() >= 2][["ShortName", "Income", "cluster", "Region"]]
    method_box("**Countries two or more steps away from their income group.** Oil-rich economies with weak social "
               "outcomes fall into the low clusters; this is the same pattern as the large negative residuals of "
               "Part 2.\n\n**Robustness (E3.1):** 3 algorithms × 20 seeds. ARI = adjusted Rand index (1 = identical "
               "partitions). Vietnam is 'Emerging' in most K-means runs but rarely with Gaussian mixtures and never "
               "with Ward: it sits on the boundary between 'Transition' and 'Emerging'.",
               "Mismatches and robustness",
               mism.rename(columns={"ShortName": "country"}).style.hide(axis="index"))

    # 3.3 · development twins (E3.2)
    soc = twins[twins.space == "same social outcomes"]
    inc = twins[twins.space == "same income"]
    takeaway(f"Vietnam's income peers are {', '.join(inc.country.head(3))}; its social-outcome twins are "
             f"<em>{', '.join(soc.country.head(3))}</em>, {soc.gdp_ratio_vs_vn.min():.1f}–"
             f"{soc.gdp_ratio_vs_vn.max():.1f}× richer",
             "Nearest neighbours by GDP per head alone vs by 10 social indicators without income "
             "(life expectancy, child mortality, fertility, schooling, internet, water, electricity, urbanisation).")
    a, b = st.columns(2)
    for col, part, title, color in ((a, inc, "Same income", k.GREY), (b, soc, "Same social outcomes", k.BLUE)):
        fig = go.Figure(go.Bar(x=part.gdp_ratio_vs_vn, y=part.country, orientation="h", marker_color=color,
                               text=[f"{v:.1f}× · {le:.0f} yrs" for v, le in zip(part.gdp_ratio_vs_vn, part.life_exp)],
                               textposition="inside" if part.gdp_ratio_vs_vn.min() > 2 else "outside",
                               textfont=dict(color="#fff" if part.gdp_ratio_vs_vn.min() > 2 else k.INK),
                               hovertemplate="%{y}: %{x:.1f}× Vietnam's GDP per head<extra></extra>"))
        fig.add_vline(x=1, line=dict(color=VN_COLOR, width=2), annotation_text="Vietnam = 1×",
                      annotation_position="bottom right", annotation_font_color=VN_COLOR)
        fig.update_yaxes(autorange="reversed")
        fig.update_xaxes(type="log", title="GDP per head relative to Vietnam (log)", range=[-0.15, 1.3])
        chart(fig.update_layout(title=f"{title} · bar label: income ratio · life expectancy"), 340, legend=False,
              target=col)

    # 3.4 · what separates Vietnam from 'Emerging' (E3.3)
    g = gaps[(gaps.versus == "Emerging")].dropna(subset=["gap_sd"]).sort_values("gap_sd")
    urb = g.set_index("indicator").loc["urban"]
    fold = st.expander(f"What separates Vietnam from the 'Emerging' cluster: income and urbanisation "
                       f"({urb.vietnam:.0f} % urban vs {urb.cluster_median:.0f} %)")
    fold.markdown("Vietnam minus the cluster median, in standard deviations across countries (log scale where "
                  "marked). Red: gaps of half a standard deviation or more.")
    fig = go.Figure(go.Bar(x=g.gap_sd, y=[LABELS[i].split(" (")[0] + (" (log)" if lg else "") for i, lg in
                                         zip(g.indicator, g.log)], orientation="h",
                           marker_color=[VN_COLOR if abs(v) >= .5 else k.GREY for v in g.gap_sd],
                           customdata=np.c_[g.vietnam, g.cluster_median],
                           hovertemplate="%{y}: %{x:+.2f} SD<br>Vietnam %{customdata[0]:,.1f} · cluster "
                                         "%{customdata[1]:,.1f}<extra></extra>"))
    fig.add_vline(x=0, line=dict(color=k.INK, width=1))
    fig.update_xaxes(title="Vietnam − 'Emerging' median (SD)")
    chart(fig, 460, legend=False, target=fold)

    # 3.5 · answer
    takeaway("The answer: <em>richer mostly means more developed</em>, but policy shifts the whole curve")
    insights([
        ("Answer.", "Income alone explains about two thirds of the differences between countries (Part 2). The rest "
         "is real: at the same income, life expectancy rose ~5 years worldwide since 1990, and Vietnam lives "
         "~10 years longer than its income predicts."),
        ("Implications (suggestions, not causal claims).", "Judge countries on social outcomes, not only GDP. For "
         "Vietnam: child mortality, urbanisation, and a lower-carbon growth path, since it already emits ~3× what "
         "its income predicts."),
        ("Limits.", "Data ends in 2014; poorer countries report less; associations, not causal effects; country "
         "medians are not population-weighted; clusters cut a continuum."),
        ("Your question?", "The Lab tabs (Countries, Models, Clusters) answer follow-up questions live."),
    ])

    bridge("Does richer mean more developed? Mostly yes, but not only: look with data, not only with income.")

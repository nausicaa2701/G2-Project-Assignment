"""Part 3 · SO WHAT: clustering, development twins and gaps, E3.1-E3.3 ("look with data, not only with income")."""
from itertools import combinations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.metrics import adjusted_rand_score
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler

from wdi.story.common import (CLUSTER_LOG, CLUSTER_NAMES, CLUSTER_VARS, GREY, SOCIAL_VARS, VN, VN_COLOR, _save,
                              snapshot)


def cluster_matrix(snap, vars_=CLUSTER_VARS, log_vars=CLUSTER_LOG, min_cov=0.7):
    """Countries with >= min_cov of vars_, log-transformed, income-group median imputed, standardised."""
    d = snap[["CountryCode", "ShortName", "Region", "Income"] + vars_]
    d = d[d[vars_].notna().mean(axis=1) >= min_cov].reset_index(drop=True)
    X = d[vars_].copy()
    for v in set(log_vars) & set(vars_):
        X[v] = np.log10(X[v].clip(lower=1e-2))
    X = X.fillna(X.groupby(d.Income, observed=True).transform("median")).fillna(X.median())
    return d, X, StandardScaler().fit_transform(X)


def fit_clusters(Z, gdp, algo="K-means", k=4, seed=42):
    """Cluster labels renumbered 1..k by the cluster's median GDP per capita (1 = poorest)."""
    if algo == "K-means":
        lab = KMeans(k, n_init=20, random_state=seed).fit_predict(Z)
    elif algo == "Gaussian mixture":
        lab = GaussianMixture(k, n_init=5, random_state=seed).fit(Z).predict(Z)
    else:
        lab = AgglomerativeClustering(k, linkage="ward").fit_predict(Z)
    order = pd.Series(np.asarray(gdp)).groupby(lab).median().rank(method="first").astype(int)
    return pd.Series(lab).map(order).to_numpy()


def income_agreement(lab, income):
    """Share of countries in the income group that dominates their cluster (as on the app's Clusters page)."""
    ct = pd.crosstab(lab, np.asarray(income))
    return ct.max(axis=1).sum() / len(lab)


def e3_1_cluster_robustness(seeds=range(20), k=4):
    """E3.1: 3 algorithms x 20 seeds. ARI vs the reference (K-means, seed 42, the app default), share of runs
    with Vietnam in the 'Emerging' cluster, and agreement with World Bank income groups."""
    snap = snapshot()
    d, X, Z = cluster_matrix(snap)
    ref = fit_clusters(Z, X.gdp_pc)
    vi = d.index[d.CountryCode == VN][0]
    rows, labs = [], {}
    for algo in ["K-means", "Gaussian mixture", "Agglomerative (Ward)"]:
        for s in seeds:
            lab = fit_clusters(Z, X.gdp_pc, algo, k, s)
            labs[(algo, s)] = lab
            rows.append({"algorithm": algo, "seed": s, "ari_vs_reference": adjusted_rand_score(ref, lab),
                         "vn_cluster": CLUSTER_NAMES.get(lab[vi], lab[vi]), "agreement": income_agreement(lab, d.Income)})
    runs = pd.DataFrame(rows)
    pair = {a: np.mean([adjusted_rand_score(labs[(a, i)], labs[(a, j)]) for i, j in combinations(seeds, 2)])
            for a in runs.algorithm.unique()}
    summ = runs.groupby("algorithm").agg(ari_vs_reference=("ari_vs_reference", "mean"),
                                         agreement=("agreement", "mean"),
                                         vn_emerging_share=("vn_cluster", lambda c: (c == "Emerging").mean()))
    summ["ari_between_seeds"] = pd.Series(pair)
    # how stable is each country's cluster across all 60 runs (share of runs in its modal cluster)
    allab = np.vstack(list(labs.values()))
    stab = pd.DataFrame({"CountryCode": d.CountryCode, "ShortName": d.ShortName,
                         "reference": pd.Series(ref).map(CLUSTER_NAMES),
                         "modal_share": [np.bincount(allab[:, i]).max() / len(allab) for i in range(len(d))]})
    return summ.reset_index(), runs, stab


def e3_2_twins(n=5, country=VN):
    """E3.2: nearest neighbours by GDP per capita alone vs by social outcomes only (no income in the space)."""
    snap = snapshot()
    d, X, Z = cluster_matrix(snap, SOCIAL_VARS, ["u5_mort"])
    i = d.index[d.CountryCode == country][0]
    gdp = np.log10(snap.set_index("CountryCode").loc[d.CountryCode, "gdp_pc"]).to_numpy()
    dist_soc = np.sqrt(((Z - Z[i]) ** 2).sum(axis=1))
    dist_gdp = np.abs(gdp - gdp[i])
    rows = []
    for space, dist in [("same income", dist_gdp), ("same social outcomes", dist_soc)]:
        order = [j for j in np.argsort(dist) if j != i and not np.isnan(dist[j])][:n]
        for r, j in enumerate(order, 1):
            rows.append({"space": space, "rank": r, "CountryCode": d.CountryCode[j], "country": d.ShortName[j],
                         "distance": dist[j], "gdp_pc": 10 ** gdp[j], "gdp_ratio_vs_vn": 10 ** (gdp[j] - gdp[i]),
                         "life_exp": snap.set_index("CountryCode").at[d.CountryCode[j], "life_exp"]})
    return pd.DataFrame(rows)


def e3_3_gaps(country=VN):
    """E3.3: Vietnam minus the median of the 'Emerging' and 'Advanced' clusters, per indicator, in raw units and
    in standard deviations of the (log-transformed where noted) indicator across countries."""
    snap = snapshot()
    d, X, Z = cluster_matrix(snap)
    lab = fit_clusters(Z, X.gdp_pc)
    i = d.index[d.CountryCode == country][0]
    raw = snap.set_index("CountryCode").loc[d.CountryCode, CLUSTER_VARS].reset_index(drop=True)
    rows = []
    for c in (3, 4):
        med_x, med_raw = X[lab == c].median(), raw[lab == c].median()
        for v in CLUSTER_VARS:
            rows.append({"versus": CLUSTER_NAMES[c], "indicator": v, "log": v in CLUSTER_LOG,
                         "vietnam": raw.at[i, v], "cluster_median": med_raw[v],
                         # no gap when Vietnam's own value was imputed (enrol_secondary is missing)
                         "gap_sd": (X.at[i, v] - med_x[v]) / X[v].std() if pd.notna(raw.at[i, v]) else np.nan})
    out = pd.DataFrame(rows)
    out["abs_gap_sd"] = out.gap_sd.abs()
    return out.sort_values(["versus", "abs_gap_sd"], ascending=[True, False]).reset_index(drop=True)



# ------------------------------------------------------------------ figures
def fig_clusters(summ):
    fig, ax = plt.subplots(figsize=(8, 3.4))
    x = np.arange(len(summ))
    for j, (c, lab) in enumerate([("ari_between_seeds", "ARI between seeds"), ("ari_vs_reference", "ARI vs reference"),
                                  ("agreement", "agreement with income groups"), ("vn_emerging_share", "Vietnam in 'Emerging'")]):
        ax.bar(x + (j - 1.5) * 0.2, summ[c], 0.2, label=lab, color=VN_COLOR if c.startswith("vn") else None)
    ax.set_xticks(x, summ.algorithm, fontsize=9)
    ax.set(ylim=(0, 1.05), title="E3.1 Cluster robustness over 20 seeds per algorithm")
    ax.legend(fontsize=8, frameon=False, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.12))
    _save(fig, "E3_1_cluster_robustness.png")


def fig_gaps(d):
    g = d[d.versus == "Emerging"].dropna(subset=["gap_sd"]).sort_values("gap_sd")
    fig, ax = plt.subplots(figsize=(7, 4.4))
    ax.barh(g.indicator + np.where(g.log, " (log)", ""), g.gap_sd,
            color=[VN_COLOR if abs(v) >= 0.5 else GREY for v in g.gap_sd])
    ax.axvline(0, color="black", lw=0.8)
    ax.set(xlabel="Vietnam minus 'Emerging' cluster median, in SD", title="E3.3 Where Vietnam differs from its cluster")
    ax.title.set_fontsize(10)
    _save(fig, "E3_3_gaps.png")


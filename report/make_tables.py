"""Write the LaTeX tables of FINAL_REPORT.tex from results/ so no number is typed by hand.

python report/make_tables.py   (after `python -m wdi.story`)
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
R, S, OUT = ROOT / "results", ROOT / "results" / "story", Path(__file__).parent / "tables"
THEME = {"gdp_pc": "Economy", "gdp_pc_ppp": "Economy", "gdp_growth": "Economy", "inflation": "Economy",
         "unemployment": "Economy", "trade_open": "Economy", "gini": "Economy", "poverty_190": "Economy",
         "population": "Demography", "pop_growth": "Demography", "urban": "Demography", "fertility": "Demography",
         "age65": "Demography", "age0_14": "Demography", "female_lfp": "Demography", "life_exp": "Health",
         "infant_mort": "Health", "u5_mort": "Health", "health_exp": "Health", "safe_water": "Health",
         "enrol_primary": "Education", "enrol_secondary": "Education", "enrol_tertiary": "Education",
         "literacy": "Education", "edu_exp": "Education", "co2_pc": "Environment", "energy_pc": "Environment",
         "forest": "Environment", "renewables": "Environment", "electricity": "Technology", "internet": "Technology",
         "mobile": "Technology"}


def tt(s):
    return r"\texttt{" + str(s).replace("_", r"\_") + "}"


def esc(s):
    return str(s).replace("&", r"\&").replace("%", r"\%").replace("_", r"\_")


def num(x, d=None):
    """Compact number: d decimals if given, else ~3 significant digits with thousands separators."""
    if pd.isna(x):
        return "--"
    if d is not None:
        return f"{x:,.{d}f}"
    a = abs(x)
    if a >= 1000:
        return f"{x:,.0f}"
    if a >= 100:
        return f"{x:.0f}"
    if a >= 10:
        return f"{x:.1f}"
    if a >= 1:
        return f"{x:.2f}"
    return f"{x:.3f}" if a > 0 else "0"


def write(name, header, rows, spec, size=r"\small"):
    body = "\n".join(" & ".join(r) + r" \\" for r in rows)
    OUT.mkdir(exist_ok=True)
    (OUT / f"{name}.tex").write_text(
        f"{size}\n\\begin{{tabular}}{{{spec}}}\n\\toprule\n{' & '.join(header)} \\\\\n\\midrule\n{body}\n"
        f"\\bottomrule\n\\end{{tabular}}\n", encoding="utf-8")


def main():
    d = pd.read_csv(S / "A2_summary_stats.csv")
    write("summary", ["Indicator", "Theme", "n", r"Miss.\,\%", "Mean", "Median", "Std", "Min", "Max", "Skew"],
          [[tt(r.indicator), THEME[r.indicator], f"{r['count']:.0f}", num(r["missing_%"], 1), num(r["mean"]),
            num(r["median"]), num(r["std"]), num(r["min"]), num(r["max"]), num(r["skew"], 2)] for _, r in d.iterrows()],
          "llrrrrrrrr", r"\footnotesize")

    d = pd.read_csv(S / "A2_missing_impact.csv")
    write("missing", ["Indicator", r"Miss.\,\%", "Mean (rep.)", "Mean (imp.)", r"Shift\,\%", "Median (rep.)",
                      "Median (imp.)", "Cov. LI", "Cov. LMI", "Cov. UMI", "Cov. HI"],
          [[tt(r.indicator), num(r["missing_%"], 1), num(r.mean_reporters), num(r.mean_imputed),
            f"{r['mean_shift_%']:+.1f}", num(r.median_reporters), num(r.median_imputed)]
           + [f"{r[f'coverage {g}']:.0f}" for g in ["Low income", "Lower middle income", "Upper middle income",
                                                     "High income"]] for _, r in d.iterrows()],
          "lrrrrrrrrrr", r"\footnotesize")

    d = pd.read_csv(S / "A3_missing_corr.csv")
    write("corr", ["Pair", r"$n$ pairwise", r"$\rho$ pairwise", r"$n$ imputed", r"$\rho$ imputed", r"$\Delta\rho$"],
          [[tt(r.pair).replace("~", r"$\sim$"), str(r.n_pairwise), num(r.rho_pairwise, 2), str(r.n_imputed),
            num(r.rho_imputed, 2), f"{r.rho_imputed - r.rho_pairwise:+.2f}"] for _, r in d.iterrows()], "lrrrrr")

    d = pd.read_csv(S / "A3_outliers.csv")
    d = d[d.n_outliers > 0]
    write("outliers", ["Indicator", "Scale", r"$n$", "Outliers", "Most extreme (value)"],
          [[tt(r.indicator), r.scale, str(r.n), str(r.n_outliers), esc(r.examples)] for _, r in d.iterrows()],
          "llrrp{9cm}", r"\footnotesize")

    d = pd.read_csv(S / "E1_1_sigma.csv")
    rows = []
    for v, g in d.groupby("indicator", sort=False):
        g = g.sort_values("Year")
        ch = 100 * (g.cv.iloc[-1] / g.cv.iloc[0] - 1)
        rows.append([tt(v), f"{g.Year.iloc[0]:.0f}", num(g.cv.iloc[0], 2), f"{g.Year.iloc[-1]:.0f}",
                     num(g.cv.iloc[-1], 2), f"{ch:+.0f}"])
    write("sigma", ["Indicator", "First year", "CV", "Last year", "CV", r"Change\,\%"], rows, "lrrrrr")

    d = pd.read_csv(S / "E1_2_beta.csv")
    write("beta", ["Indicator", "Period", r"$n$", r"$\beta$", "95\\% CI", r"$r$", r"$p$", "Vietnam change/yr"],
          [[tt(r.indicator), r.period, str(r.n), num(r.beta, 3), f"[{r.ci_low:.3f}, {r.ci_high:.3f}]", num(r.r, 2),
            f"{r.p:.3f}" if r.p >= 0.001 else "$<$0.001", num(r.vn_change, 2)] for _, r in d.iterrows()],
          "llrrrrrr")

    d = pd.read_csv(S / "E1_3_robustness.csv")
    write("robust", ["Indicator", "Sample", r"$n$ (1990/2013)", "CV 1990", "CV 2013", r"Change\,\%", "Direction"],
          [[tt(r.indicator), r.version, f"{r.n_start}/{r.n_end}", num(r.cv_start, 2), num(r.cv_end, 2),
            f"{r['change_%']:+.0f}", r.direction] for _, r in d.iterrows()], "lllrrrl", r"\footnotesize")

    d = pd.read_csv(S / "E2_1_r2_layers.csv")
    write("r2", ["Theme", "\\ding{172} Income only", "\\ding{173} All features", "\\ding{174} Best model", "Best"],
          [[r.theme, f"{r['income only mean']:.2f} $\\pm$ {r['income only std']:.3f}",
            f"{r['all features mean']:.2f} $\\pm$ {r['all features std']:.3f}",
            f"{r['best mean']:.2f} $\\pm$ {r['best std']:.3f}", r["best model"]] for _, r in d.iterrows()]
          + [[r"\textit{Mean}", f"{d['income only mean'].mean():.2f}", f"{d['all features mean'].mean():.2f}",
              f"{d['best mean'].mean():.2f}", ""]], "lrrrl")

    d = pd.read_csv(S / "E2_2_residuals_focus.csv")
    rows = []
    for _, r in d.sort_values(["theme", "rank"]).iterrows():
        res = f"{r.residual:.1f}$\\times$" if r.unit != "units" else f"{r.residual:+.1f}"
        name = r"\textbf{" + esc(r.ShortName) + "}" if r.CountryCode == "VNM" else esc(r.ShortName)
        rows.append([r.theme, tt(r.target), name, num(r.actual), num(r.predicted), res, f"{r['rank']}/{r['of']}"])
    write("resid", ["Theme", "Target", "Country", "Actual", "Predicted", "Residual", "Rank"], rows, "lllrrrr",
          r"\footnotesize")

    d = pd.read_csv(S / "E2_3_fixed_effects.csv")
    write("fe", ["Model", "Years per 10$\\times$ GDP pc", "SE", "95\\% CI", "Obs.", "Countries"],
          [[r.model, num(r.slope_per_10x, 2), num(r.se, 2), f"[{r.ci_low:.2f}, {r.ci_high:.2f}]", f"{r.n_obs:,}",
            str(r.n_countries)] for _, r in d.iterrows()], "lrrrrr")

    d = pd.read_csv(S / "E3_1_cluster_robustness.csv")
    write("clu", ["Algorithm", "ARI between seeds", "ARI vs reference", "Agreement w/ income", "Vietnam `Emerging'"],
          [[r.algorithm, num(r.ari_between_seeds, 2), num(r.ari_vs_reference, 2), f"{100 * r.agreement:.0f}\\%",
            f"{100 * r.vn_emerging_share:.0f}\\%"] for _, r in d.iterrows()], "lrrrr")

    d = pd.read_csv(S / "E3_2_twins.csv")
    a, b = d[d.space == "same income"], d[d.space == "same social outcomes"]
    write("twins", ["Rank", "Same income", "Life exp.", "Same social outcomes", "Income vs VN", "Life exp."],
          [[str(i + 1), esc(x.country), num(x.life_exp, 1), esc(y.country), f"{y.gdp_ratio_vs_vn:.1f}$\\times$",
            num(y.life_exp, 1)] for i, ((_, x), (_, y)) in enumerate(zip(a.iterrows(), b.iterrows()))], "rlrlrr")

    d = pd.read_csv(S / "E3_3_gaps.csv").dropna(subset=["gap_sd"])
    e, v = d[d.versus == "Emerging"].set_index("indicator"), d[d.versus == "Advanced"].set_index("indicator")
    write("gaps", ["Indicator", "Vietnam", "Emerging median", "Gap (SD)", "Advanced median", "Gap (SD)"],
          [[tt(i) + (" (log)" if r.log else ""), num(r.vietnam), num(r.cluster_median), f"{r.gap_sd:+.2f}",
            num(v.at[i, "cluster_median"]), f"{v.at[i, 'gap_sd']:+.2f}"] for i, r in e.iterrows()], "lrrrrr",
          r"\footnotesize")

    rows = []
    for mode in ["snapshot", "panel"]:
        s = pd.read_csv(R / f"summary_{mode}.csv")
        for t, g in s.groupby("theme"):
            best = g.iloc[0]
            lin, rf = g.set_index("model").loc["Linear"], g.set_index("model").loc["RandomForest"]
            rows.append([mode.capitalize(), t, f"{lin.r2_mean:.3f}", f"{rf.r2_mean:.3f}", best.model,
                         f"{best.r2_mean:.3f} $\\pm$ {best.r2_std:.3f}", num(best.mae_mean, 3), num(best.rmse_mean, 3)])
    write("models", ["Data", "Theme", "Linear $R^2$", "RF $R^2$", "Best model", "Best $R^2$", "MAE", "RMSE"], rows,
          "llrrlrrr", r"\footnotesize")

    imp = pd.read_csv(R / "importance_snapshot.csv")
    rows = [[t, g.model.iloc[0], ", ".join(f"{tt(f)} ({x:.2f})" for f, x in zip(g.feature[:3], g.importance[:3]))]
            for t, g in imp.groupby("theme", sort=False)]
    write("importance", ["Theme", "Model", "Top-3 features (permutation importance, drop in $R^2$)"], rows,
          "llp{10cm}", r"\footnotesize")
    print("wrote", sorted(p.name for p in OUT.glob("*.tex")))


if __name__ == "__main__":
    main()

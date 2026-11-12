"""Home page: title, the answer in four numbers, links to the three parts, the team.

Headline numbers are read from results/story/ (the same files as the Findings tabs), so the page never drifts.
"""
import base64
from pathlib import Path

import streamlit as st

from ui.core import VN, goto, grid, load_results, scroll_top

APP_URL = "https://g2-project-assignment.streamlit.app/"
QR = Path(__file__).parent / "assets" / "qr_app.png"

MEMBERS = [("Le Thi Hong Cuc", "2470882"), ("Phan Van Nguyen Khanh", "2470883"), ("Nguyen Tuong Phuc", "2470886")]

ROLES = {
    "Le Thi Hong Cuc": ("Data and the role of income", [
        "Data audit and preprocessing pipeline (A, B)",
        "RQ2 · Why: income layers, residuals, fixed effects",
        "Data and Findings 2 pages; reproducibility (notebook, Makefile, tests)",
        "Report: data, preprocessing and RQ2 chapters"]),
    "Phan Van Nguyen Khanh": ("Exploration and convergence", [
        "Exploratory analysis, trends and group comparisons",
        "RQ1 · What changed: σ- and β-convergence",
        "Findings 1 page; Lab Countries",
        "Report: background, EDA and RQ1 chapters"]),
    "Nguyen Tuong Phuc": ("Models, clusters and Vietnam", [
        "Suite of 19 models with country-grouped cross-validation",
        "RQ3 · So what: clustering, Vietnam and its peers",
        "Findings 3 page; Lab Models and Clusters",
        "Report: methods, RQ3 and discussion chapters"]),
}


@st.cache_data(show_spinner=False)
def _qr():
    return base64.b64encode(QR.read_bytes()).decode()


@st.cache_data(show_spinner=False)
def _headlines():
    from ui.part3 import _reference

    h = {"agree": _reference()[3]}
    r2 = load_results("story/part2/E2_1_r2_layers.csv")   # same source as the "2 · Why" tab
    if r2 is not None:
        inc, best = r2[r2.layer == "income"].r2_mean, r2[r2.layer == "best"].r2_mean
        h.update(r2_lo=inc.min(), r2_hi=inc.max(), r2_mean=inc.mean(), r2_best=best.mean())
    fe = load_results("story/E2_3_fixed_effects.csv")
    if fe is not None:
        s = fe.set_index("model").slope_per_10x
        h.update(within=s[s.index.str.contains("fixed")].iloc[0], between=s[s.index.str.contains("Between")].iloc[0])
    res = load_results("story/E2_2_residuals_focus.csv")
    if res is not None:
        v = res[res.CountryCode == VN].set_index("theme")
        h.update(vn_le=v.at["Health", "residual"], vn_co2=v.at["Environment", "residual"])
    sig = load_results("story/E1_1_sigma.csv")
    if sig is not None:
        g = sig[sig.indicator == "life_exp"].sort_values("Year").cv
        h["le_cv"] = 1 - g.iloc[-1] / g.iloc[0]
    return h


def page():
    scroll_top()
    h = _headlines()
    st.markdown(
        '<div class="hero"><div class="eyebrow">Group G2 · Data Analytics · HCMUT</div>'
        '<h1>Does richer mean<br>more developed?</h1>'
        '<p>A data-mining study of the World Bank\'s development indicators: 214 countries, 32 indicators, '
        '1960–2014.</p></div>', unsafe_allow_html=True)

    # the answer in four numbers (same sources as the Findings tabs)
    stats = []
    if "r2_mean" in h:
        stats.append((f"{h['r2_mean']:.0%}", "of the differences between countries are explained by income alone."))
    stats.append((f"−{h.get('le_cv', .47):.0%}", "spread of life expectancy between countries. The income gap is as wide "
                                                 "as in 1990."))
    if "within" in h:
        stats.append((f"+{h['within']:.0f} yrs", f"of life when a country grows 10× richer, against "
                                                 f"+{h['between']:.0f} years between rich and poor countries."))
    if "vn_le" in h:
        stats.append((f"{h['vn_le']:+.0f} yrs", "Vietnam lives longer than its income predicts, more than any other "
                                                "country."))
    st.markdown('<div class="section-title">Mostly yes. But not only.</div>'
                f'<div class="section-sub">Income groups match data-driven clusters for {h["agree"]:.0%} of countries: '
                'development is a continuum, and policy shifts the curve.</div>', unsafe_allow_html=True)
    grid([f'<div class="card stat"><div class="num">{n}</div><div class="txt">{t}</div></div>' for n, t in stats],
         n=2)

    st.markdown('<div class="section-title">Explore</div>', unsafe_allow_html=True)
    parts = [("data", "exploration", "Data", "What is in the data, what is missing, and how it was cleaned."),
             ("findings", "what", "Findings", "What changed, why, and what it means for Vietnam."),
             ("lab", "countries", "Lab", "Any indicator, country or model, recomputed live.")]
    for col, (parent, slug, t, d) in zip(st.columns(3), parts):   # each card keeps its button when stacked
        col.markdown(f'<div class="card explore"><div class="t">{t}</div><div class="d">{d}</div></div>',
                     unsafe_allow_html=True)
        if col.button(f"Open {t} ›", key=f"go_{parent}", type="tertiary"):
            goto(parent, slug)

    st.markdown('<div class="section-title">Instructor</div>'
                '<div class="section-sub">Data Analytics course, Faculty of Computer Science and Engineering, '
                'Ho Chi Minh City University of Technology.</div>', unsafe_allow_html=True)
    grid(['<div class="card"><div class="t">Dr. Nguyen Thi Ai Thao</div><div class="id">Lecturer</div>'
          '<div class="d">Data Analytics · November 2026</div></div>'], n=3)

    st.markdown('<div class="section-title">Team</div>'
                '<div class="section-sub">Equal contribution: each member led one strand end to end and reviewed '
                'the other two.</div>', unsafe_allow_html=True)
    grid([f'<div class="card"><div class="t">{n}</div><div class="id">{i}</div><div class="d">{ROLES[n][0]}</div></div>'
          for n, i in MEMBERS])
    with st.expander("Who did what"):
        grid([f'<div class="card contrib"><div class="t">{n}</div><ul>'
              + "".join(f"<li>{x}</li>" for x in ROLES[n][1]) + '</ul><div class="id">33.3 %</div></div>'
              for n, _ in MEMBERS])

    st.markdown(f'<div class="footer"><div>'
                'Source: World Bank, World Development Indicators (Kaggle release).<br>'
                'Results are associations, not causal effects; country medians are not population-weighted.</div>'
                # clicking the QR toggles a hidden checkbox: CSS shows it large and centred; click again to close
                f'<input type="checkbox" id="qr-zoom" class="qr-toggle"><label for="qr-zoom" class="qr">'
                f'<img src="data:image/png;base64,{_qr()}" alt="QR code to {APP_URL}"><span>Tap to enlarge</span></label>'
                f'<label for="qr-zoom" class="qr-overlay"><img src="data:image/png;base64,{_qr()}" '
                f'alt="QR code to {APP_URL}"><span>Scan to open the app · tap anywhere to close</span></label></div>',
                unsafe_allow_html=True)

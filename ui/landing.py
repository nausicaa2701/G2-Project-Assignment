"""Home page: title, group information, a TL;DR of the findings and links to the three parts.

Headline numbers are read from results/story/ (the same files as the Findings tabs), so the page never drifts.
"""
import streamlit as st

from ui.core import VN, goto, grid, load_results, scroll_top, tiles

MEMBERS = [("Le Thi Hong Cuc", "2470882"), ("Phan Van Nguyen Khanh", "2470883"), ("Nguyen Tuong Phuc", "2470886")]


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
        '<div class="home-head"><div class="eyebrow">Data Analytics · Faculty of Computer Science and Engineering · '
        'Ho Chi Minh City University of Technology</div>'
        '<h1>Does richer mean more developed?</h1>'
        '<div class="sub">A data-mining study of the World Development Indicators, 1960–2014</div></div>',
        unsafe_allow_html=True)

    members = "<br>".join(f"{n} · {i}" for n, i in MEMBERS)
    st.markdown(
        '<div class="meta">'
        f'<div class="card"><div class="k">Group G2</div><div class="v">{members}</div></div>'
        '<div class="card"><div class="k">Lecturer</div><div class="v">Dr. Nguyen Thi Ai Thao<br>November 2026</div></div>'
        '<div class="card"><div class="k">Data</div><div class="v">World Bank World Development Indicators '
        '(Kaggle release)<br>214 countries · 32 indicators · 55 years</div></div>'
        '</div>', unsafe_allow_html=True)

    bullets = []
    if "r2_lo" in h:
        bullets.append(f"<b>Mostly yes.</b> Income alone explains <em>{h['r2_lo']:.0%}–{h['r2_hi']:.0%}</em> of the "
                       f"differences between countries (mean {h['r2_mean']:.0%}); 19 machine-learning models only "
                       f"reach {h['r2_best']:.0%}.")
    bullets.append(f"<b>Health converged, income did not.</b> The spread of life expectancy between countries fell "
                   f"by <em>{h.get('le_cv', .47):.0%}</em>, while the spread of income did not change.")
    if "within" in h:
        bullets.append(f"<b>Being rich matters more than getting rich.</b> Ten times more income goes with "
                       f"+{h['between']:.0f} years of life between countries, but only <em>+{h['within']:.0f} "
                       f"years</em> within a country over time.")
    bullets.append(f"<b>Income groups are a rough guide.</b> Data-driven clusters match them for "
                   f"<em>{h['agree']:.0%}</em> of countries; development looks like a continuum, not four boxes.")
    if "vn_le" in h:
        bullets.append(f"<b>Vietnam</b> lives <em>{h['vn_le']:+.0f} years</em> longer than its income predicts, the "
                       f"best of all countries, but emits {h['vn_co2']:.1f}× the CO₂.")
    st.markdown('<div class="tldr"><h3>TL;DR</h3><ul>' + "".join(f"<li>{b}</li>" for b in bullets) + "</ul></div>",
                unsafe_allow_html=True)

    st.markdown('<div class="section-title">The data at a glance</div>', unsafe_allow_html=True)
    tiles([("Raw observations", "5.66 M", "country × indicator × year"),
           ("Countries", "214", "33 regional aggregates removed"),
           ("Indicators", "32", "selected from 1,344, in six themes"),
           ("Missing cells", "42 %", "after filling short gaps")])

    st.markdown('<div class="section-title">Explore</div>', unsafe_allow_html=True)
    parts = [("data", "exploration", "Data", "What is in the data, what is missing, and how it was cleaned."),
             ("findings", "what", "Findings", "Three questions: what changed, why, and what it means for Vietnam."),
             ("lab", "trends", "Lab", "Any indicator, country or model, recomputed live.")]
    grid([f'<div class="card"><div class="t">{t}</div><div class="d">{d}</div></div>' for _, _, t, d in parts])
    for col, (parent, slug, t, _) in zip(st.columns(3), parts):
        if col.button(f"Open {t} →", key=f"go_{parent}", type="tertiary"):
            goto(parent, slug)

    st.markdown('<div class="footer">Source: World Bank, World Development Indicators (Kaggle release). '
                'Results are associations, not causal effects; country medians are not population-weighted.</div>',
                unsafe_allow_html=True)

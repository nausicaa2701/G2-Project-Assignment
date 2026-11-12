"""Shared UI: design system (light/dark), data loading, labels and the story helpers used by every page.

Theme-dependent values (C, BLUE, INK, GREY, LINE, PALETTE, INCOME_COLORS, CLUSTER_COLORS) are module globals that
`apply_theme()` recomputes on every rerun, so pages read them as `k.BLUE` (with `from ui import core as k`),
never as a copy taken at import time.
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from wdi.models import data_path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

# design system
# Apple-style light and dark palettes: white page, soft grey surfaces, one blue accent, Vietnam always in red.
# The toggle (top-right) stores its value in session state; app.py calls apply_theme() on every rerun.
MODES = {
    False: dict(bg="#ffffff", card="#f5f5f7", ink="#1d1d1f", grey="#6e6e73", line="#d2d2d7", grid="#e8e8ed",
                field="#e8e8ed", pill="#ffffff", glass="rgba(255,255,255,.8)", blue="#0071e3", soft="#a8cdf7",
                template="plotly_white"),
    True:  dict(bg="#000000", card="#1c1c1e", ink="#f5f5f7", grey="#98989d", line="#38383a", grid="#2c2c2e",
                field="#2c2c2e", pill="#636366", glass="rgba(22,22,23,.8)", blue="#2997ff", soft="#0a4a8f",
                template="plotly_dark"),
}
FONT = '-apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", Inter, "Helvetica Neue", "Segoe UI", Arial, sans-serif'
INCOME_ORDER = ["Low income", "Lower middle income", "Upper middle income", "High income"]
# Vietnam is the recurring case study: always the same red on every story chart.
VN, VN_COLOR = "VNM", "#c0392b"
DARK, C, BLUE, INK, GREY, LINE = False, MODES[False], "", "", "", ""
INCOME_COLORS, CLUSTER_COLORS, PALETTE = {}, [], []


def apply_theme():
    """Recompute the palette for the current mode and inject the CSS. Call once per run, before any page."""
    global DARK, C, BLUE, INK, GREY, LINE, INCOME_COLORS, CLUSTER_COLORS, PALETTE
    DARK = st.session_state.get("dark", False)
    C = MODES[DARK]
    BLUE, INK, GREY, LINE = C["blue"], C["ink"], C["grey"], C["line"]
    INCOME_COLORS = dict(zip(INCOME_ORDER, ["#ff6b3d", "#ffb340", "#30b0c7", BLUE]))
    CLUSTER_COLORS = ["#ff6b3d", "#ffb340", "#30b0c7", BLUE, "#af52de", "#ff2d55", "#34c759", GREY]
    PALETTE = [BLUE, "#ffb340", "#30b0c7", "#ff6b3d", "#af52de", "#ff2d55", "#34c759", "#a2845e"]
    px.defaults.color_discrete_sequence = PALETTE
    c = C
    st.markdown(f"""<style>
    @import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap");
    html, body, [class*="css"], .stMarkdown, button, input, select, textarea {{ font-family: {FONT} !important;
        -webkit-font-smoothing: antialiased; }}
    .block-container {{ padding: 2.5rem 1.5rem 5rem; max-width: 1024px; }}
    .stApp {{ background: {c["bg"]}; }}
    header[data-testid="stHeader"] {{ background: {c["glass"]}; backdrop-filter: saturate(180%) blur(20px);
        -webkit-backdrop-filter: saturate(180%) blur(20px); border-bottom: 1px solid {LINE}; }}
    h1, h2, h3, h4 {{ color: {INK}; letter-spacing: -0.02em; }}
    h4 {{ font-size: 1.2rem !important; font-weight: 600 !important; margin: 3.5rem 0 .2rem !important; }}
    footer, #MainMenu {{ visibility: hidden; }}
    [data-testid="stHeaderActionElements"] {{ display: none; }}

    /* page header: centred, large, quiet */
    .hero {{ text-align: center; padding: 3.2rem 0 2.6rem; }}
    .eyebrow {{ color: {GREY}; font-weight: 600; font-size: .95rem; letter-spacing: -0.01em; margin-bottom: .7rem; }}
    .hero h1 {{ font-size: clamp(2.1rem, 5.2vw, 3.6rem); font-weight: 700; line-height: 1.07; letter-spacing: -0.035em;
               margin: 0; padding: 0; color: {INK}; }}
    .hero p {{ color: {GREY}; font-size: clamp(1.05rem, 1.7vw, 1.3rem); line-height: 1.45; max-width: 660px;
              margin: 1.1rem auto 0; }}

    /* section headings and story titles */
    .section-title {{ color: {INK}; font-size: clamp(1.6rem, 3vw, 2.25rem); font-weight: 700; letter-spacing: -0.03em;
                      line-height: 1.12; margin: 5rem 0 .4rem; }}
    .section-sub {{ color: {GREY}; font-size: 1.05rem; line-height: 1.5; margin-bottom: 1.4rem; max-width: 720px; }}
    .takeaway {{ color: {INK}; font-size: clamp(1.3rem, 2.3vw, 1.7rem); font-weight: 650; line-height: 1.22;
                 letter-spacing: -0.025em; margin: 4.5rem 0 .5rem; max-width: 880px; }}
    .takeaway em {{ font-style: normal; color: {BLUE}; }}
    .takeaway-sub {{ color: {GREY}; font-size: 1rem; line-height: 1.5; margin-bottom: 1.4rem; max-width: 720px; }}
    .bridge {{ color: {INK}; font-size: clamp(1.15rem, 2vw, 1.4rem); font-weight: 600; letter-spacing: -0.02em;
               text-align: center; padding: 3rem 0 .5rem; margin-top: 5rem; border-top: 1px solid {LINE}; }}

    /* equal-height grids of tiles and cards; column counts per breakpoint come from grid() */
    .grid {{ display: grid; gap: 16px; grid-template-columns: repeat(var(--n), minmax(0, 1fr)); margin: .6rem 0 1.2rem; }}
    @media (max-width: 900px) {{ .grid {{ grid-template-columns: repeat(var(--t), minmax(0, 1fr)); }} }}
    @media (max-width: 600px) {{ .grid {{ grid-template-columns: repeat(var(--p), minmax(0, 1fr)); gap: 12px; }} }}
    .tile, .insight, .card {{ background: {c["card"]}; border: 0; border-radius: 18px; padding: 22px 24px; }}
    .tile .k {{ color: {GREY}; font-size: .85rem; font-weight: 500; }}
    .tile .v {{ color: {INK}; font-size: 1.9rem; font-weight: 700; letter-spacing: -0.03em; line-height: 1.2; margin: .3rem 0; }}
    .tile .s {{ color: {GREY}; font-size: .82rem; line-height: 1.45; }}
    .insight b {{ display: block; color: {INK}; font-size: 1.05rem; font-weight: 600; margin-bottom: .35rem; }}
    .insight span {{ color: {GREY}; font-size: .93rem; line-height: 1.55; }}

    /* charts, tables, expanders: soft grey surfaces, no borders */
    div[data-testid="stPlotlyChart"] {{ background: {c["card"]}; border-radius: 18px; padding: 0 6px; overflow: hidden; }}
    .tbl {{ background: {c["card"]}; border-radius: 18px; overflow-x: auto; padding: 8px 16px; }}
    .tbl table {{ border-collapse: collapse; width: 100%; font-size: .86rem; color: {INK}; }}
    .tbl th {{ color: {GREY}; font-weight: 500; text-align: right; padding: .6rem .6rem; border-bottom: 1px solid {LINE};
               min-width: 4.5rem; }}
    .tbl th.row_heading {{ text-align: left; }}
    .tbl td {{ text-align: right; padding: .55rem .6rem; border-bottom: 1px solid {c["grid"]}; font-variant-numeric: tabular-nums;
               white-space: nowrap; }}
    .tbl tr:last-child td {{ border-bottom: 0; }}
    [data-testid="stExpander"] details {{ background: transparent; border: 0; border-top: 1px solid {LINE};
               border-bottom: 1px solid {LINE}; border-radius: 0; }}
    [data-testid="stExpander"] summary {{ padding-left: 0; padding-right: 0; }}
    [data-testid="stExpander"] summary, [data-testid="stExpander"] summary * {{ color: {BLUE} !important; font-weight: 500; }}
    [data-testid="stExpander"] summary, [data-testid="stExpander"] summary:hover {{ background: transparent !important; }}
    [data-testid="stMarkdownContainer"] code {{ background: {c["field"]} !important; color: {INK} !important; }}
    [data-testid="stTextInputRootElement"], [data-testid="stNumberInputContainer"], [data-testid="stTextInputRootElement"] input,
    [data-testid="stNumberInputContainer"] input, [data-testid="stNumberInputContainer"] button {{ background: {c["field"]} !important;
                color: {INK} !important; border-color: transparent !important; }}
    [data-testid="stExpander"] summary:hover p {{ text-decoration: underline; }}
    [data-testid="stExpanderDetails"] {{ padding-left: 0; padding-right: 0; }}

    /* widgets */
    .st-key-dark {{ position: fixed; top: .8rem; right: 1.4rem; z-index: 1000001; width: auto !important; }}
    .stApp, .stMarkdown, [data-testid="stWidgetLabel"] p, [data-testid="stMarkdownContainer"] p, .st-key-dark p {{ color: {INK}; }}
    [data-testid="stWidgetLabel"] p {{ font-size: .85rem; color: {GREY} !important; }}
    [data-testid="stCaptionContainer"] {{ color: {GREY} !important; }}
    .stSelectbox [role="group"], .stMultiSelect [role="group"], .stTextInput input, .stNumberInput input,
    .stNumberInput button, div[data-baseweb="input"], div[data-baseweb="select"] > div {{ background: {c["field"]} !important;
                color: {INK} !important; border-color: transparent !important; }}
    div[data-baseweb="select"] > div, .stNumberInput input, div[data-baseweb="input"] {{ border-radius: 12px !important; }}
    [role="combobox"], .stSelectbox svg, .stMultiSelect svg, .stNumberInput svg {{ color: {INK} !important; }}
    [data-testid="stSelectboxVirtualDropdown"], [role="listbox"] {{ background: {c["bg"]} !important; color: {INK} !important;
                border-color: {LINE} !important; border-radius: 12px; }}
    [role="option"] {{ color: {INK} !important; }}
    [role="option"]:hover, [role="option"][data-focused="true"] {{ background: {c["card"]} !important; }}
    [data-tag] {{ background: {c["bg"]} !important; color: {INK} !important; border: 0; border-radius: 999px !important; }}
    [data-tag] * {{ color: {INK} !important; }}
    [data-testid="stSliderThumbValue"], [data-testid="stSliderTickBarMin"], [data-testid="stSliderTickBarMax"] {{ color: {GREY}; }}
    [data-testid="stForm"] {{ border: 0; background: {c["card"]}; border-radius: 18px; padding: 1.4rem; }}
    [data-testid="stForm"] div[data-baseweb="select"] > div, [data-testid="stForm"] div[data-baseweb="input"],
    [data-testid="stForm"] .stTextInput input {{ background: {c["bg"]} !important; }}
    [data-testid="stAlert"] {{ background: {c["card"]}; color: {INK}; border: 0; border-radius: 14px; }}

    /* segmented controls: grey track, raised selected pill */
    [data-testid="stButtonGroup"] > div {{ background: {c["field"]}; border-radius: 999px; padding: 3px; gap: 2px;
                width: fit-content; max-width: 100%; flex-wrap: nowrap; overflow-x: auto; scrollbar-width: none; }}
    button[data-variant="segmented_control"] {{ background: transparent !important; color: {INK} !important; border: 0 !important;
                border-radius: 999px !important; padding: .35rem 1rem !important; box-shadow: none !important;
                flex: 0 0 auto !important; white-space: nowrap; }}
    button[data-variant="segmented_control"][data-selected="true"], button[data-variant="segmented_control"][aria-checked="true"],
    button[kind="segmented_controlActive"] {{ background: {c["pill"]} !important; color: {INK} !important;
                box-shadow: 0 1px 4px rgba(0,0,0,.12) !important; }}
    button[data-variant="segmented_control"] p {{ color: inherit !important; font-weight: 500; }}

    [data-testid="stTopNavLinkContainer"] span, header a span {{ color: {INK} !important; }}
    [data-testid="stTooltipIcon"] svg {{ color: {GREY}; }}
    .stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {{ background: {BLUE}; color: #fff;
                border: 0; border-radius: 999px; padding: .55rem 1.3rem; font-weight: 500; box-shadow: none; }}
    .stButton > button:hover, .stFormSubmitButton > button:hover {{ filter: brightness(1.08); color: #fff; }}
    .stButton > button p, .stDownloadButton > button p, .stFormSubmitButton > button p {{ color: inherit !important; }}
    .stButton > button[data-testid="stBaseButton-secondary"] {{ background: transparent; color: {BLUE}; border: 1px solid {BLUE}; }}
    .stButton > button[data-testid="stBaseButton-tertiary"] {{ background: transparent; color: {BLUE}; border: 0; padding: .2rem 0;
                min-height: 0; }}
    .stButton > button[data-testid="stBaseButton-tertiary"]:hover {{ text-decoration: underline; filter: none; }}

    /* tab bar of a parent page: centred segmented control, sticky under the header */
    [class*="st-key-tab_"] {{ position: sticky; top: 3.75rem; z-index: 999; padding: .6rem 0; background: {c["glass"]};
                backdrop-filter: saturate(180%) blur(20px); -webkit-backdrop-filter: saturate(180%) blur(20px); }}
    [class*="st-key-tab_"] [data-testid="stButtonGroup"] {{ display: flex; justify-content: center; }}
    [class*="st-key-tab_"] [data-testid="stButtonGroup"] > div {{ margin: 0 auto; }}
    iframe[height="0"] {{ display: block; }}
    .element-container:has(> iframe[height="0"]), .stElementContainer:has(> iframe[height="0"]) {{ display: none; }}
    .pager-rule {{ border-top: 1px solid {LINE}; margin: 4rem 0 1rem; }}

    /* landing page */
    .stat .num {{ color: {BLUE}; font-size: clamp(2.3rem, 5vw, 3.2rem); font-weight: 700; letter-spacing: -0.04em; line-height: 1.05; }}
    .stat .txt {{ color: {INK}; font-size: 1rem; line-height: 1.45; margin-top: .6rem; }}
    .card .t {{ color: {INK}; font-weight: 650; font-size: 1.25rem; letter-spacing: -0.02em; }}
    .card .d {{ color: {GREY}; font-size: .95rem; line-height: 1.5; margin-top: .4rem; }}
    .card .id {{ color: {GREY}; font-size: .85rem; margin-top: .25rem; }}
    .explore {{ min-height: 8.5rem; }}
    .contrib ul {{ margin: .5rem 0 1rem; padding-left: 1.1rem; color: {INK}; font-size: .9rem; line-height: 1.6; }}
    .footer {{ color: {GREY}; font-size: 1rem; padding: 2rem 0 .4rem; border-top: 1px solid {LINE}; margin-top: 5rem;
               line-height: 1.7; display: flex; justify-content: space-between; align-items: center; gap: 24px; }}
    .qr {{ flex: none; display: flex; flex-direction: column; align-items: center; gap: 6px; cursor: zoom-in; }}
    .qr-toggle {{ display: none; }}
    .qr-overlay {{ display: none; position: fixed; inset: 0; z-index: 1000002; background: {c["glass"]};
                   backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px); cursor: zoom-out;
                   flex-direction: column; align-items: center; justify-content: center; gap: 18px; }}
    .qr-toggle:checked ~ .qr-overlay {{ display: flex; }}
    .qr-overlay img {{ width: min(80vw, 80vh, 520px); height: auto; aspect-ratio: 1; background: #fff; padding: 22px;
                       border-radius: 28px; image-rendering: pixelated; box-shadow: 0 20px 60px rgba(0,0,0,.18); }}
    .qr-overlay span {{ color: {INK}; font-size: 1rem; font-weight: 500; }}
    .qr img {{ width: 104px; height: 104px; background: #fff; padding: 6px; border-radius: 12px; image-rendering: pixelated; }}
    .qr span {{ color: {GREY}; font-size: .85rem; }}

    /* touch screens: no Plotly toolbar (it covers the chart titles) */
    @media (hover: none), (max-width: 640px) {{ .modebar-container {{ display: none !important; }} }}

    /* phones */
    @media (max-width: 640px) {{
        .block-container {{ padding: 1.4rem 1rem 3rem; }}
        .hero {{ padding: 2rem 0 1.6rem; }}
        .tile, .insight, .card {{ padding: 16px 18px; border-radius: 16px; }}
        .tile .v {{ font-size: 1.4rem; }}
        .tile .s {{ font-size: .76rem; }}
        .section-title {{ margin-top: 3.2rem; }}
        .takeaway {{ margin-top: 3rem; }}
        .tbl {{ padding: 4px 10px; }}
        .tbl table {{ font-size: .8rem; }}
        .js-plotly-plot .gtitle {{ font-size: 12.5px !important; }}
        .explore {{ min-height: 0; }}
        .footer {{ flex-direction: column; align-items: flex-start; }}
        .st-key-dark {{ right: .8rem; }}
    }}
    </style>""", unsafe_allow_html=True)


def style(fig, h=420, legend=True):
    fig.update_layout(template=C["template"], height=h, font=dict(family=FONT, color=INK, size=12),
                      margin=dict(l=16, r=22, t=56, b=20), paper_bgcolor=C["card"], plot_bgcolor=C["card"],
                      title=dict(x=0.01, xanchor="left", font=dict(size=15, weight=600)), colorway=PALETTE,
                      showlegend=legend, legend=dict(orientation="h", yref="container", y=12 / h, yanchor="bottom", x=0.01, title=None,
                                                       font=dict(size=11)),
                      hoverlabel=dict(font_family=FONT, bgcolor=C["bg"], font_color=INK, bordercolor=LINE))
    fig.update_xaxes(showgrid=False, showline=False, ticks="", tickfont=dict(color=GREY),
                     title_font=dict(size=11, color=GREY))
    fig.update_yaxes(gridcolor=C["line"] if DARK else C["grid"], zeroline=False, showline=False,
                     tickfont=dict(color=GREY), title_font=dict(size=11, color=GREY))
    if any(t.type == "choropleth" for t in fig.data):
        fig.update_geos(bgcolor=C["card"], landcolor=C["grid"], showland=True, lakecolor=C["card"])
    return fig


def hero(eyebrow, title, sub):
    """Centred page header: small label, large title (keeps its <br>), one-line summary."""
    st.markdown(f'<div class="hero"><div class="eyebrow">{eyebrow}</div><h1>{title}</h1>'
                f'<p>{sub}</p></div>', unsafe_allow_html=True)


def section(title, sub=""):
    st.markdown(f'<div class="section-title">{title}</div>' + (f'<div class="section-sub">{sub}</div>' if sub else ""),
                unsafe_allow_html=True)


def table(styler):
    """Theme-aware HTML table from a pandas Styler; text columns are left-aligned, numbers right-aligned."""
    df = styler.data
    text = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])]
    if text:
        styler = styler.set_properties(subset=text, **{"text-align": "left", "white-space": "normal", "min-width": "9rem"})
        styler = styler.set_table_styles([{"selector": f"th.col{list(df.columns).index(c)}",
                                           "props": "text-align: left"} for c in text], overwrite=False)
    st.markdown(f'<div class="tbl">{styler.to_html()}</div>', unsafe_allow_html=True)


def grid(blocks, n=None, compact=False):
    """Equal-width, equal-height blocks; tablet and phone column counts keep every row full.

    compact=True (small tiles) keeps two per row on phones when the count is even.
    """
    n = n or len(blocks)
    t = n if n <= 3 else (3 if n % 3 == 0 else 2)
    p = 2 if compact and n % 2 == 0 else 1
    st.markdown(f'<div class="grid" style="--n:{n};--t:{t};--p:{p}">{"".join(blocks)}</div>', unsafe_allow_html=True)


def tiles(items):
    grid([f'<div class="tile"><div class="k">{k}</div><div class="v">{v}</div><div class="s">{s}</div></div>'
          for k, v, s in items], compact=True)


def chart(fig, h=420, legend=True, target=st):
    """style() + st.plotly_chart with the app defaults; `target` can be a column."""
    target.plotly_chart(style(fig, h, legend), width="stretch", theme=None)


def insights(items, cols=2):
    """Cards with a bold lead and a sentence, in an equal-height grid."""
    grid([f'<div class="insight"><b>{b}</b><span>{t}</span></div>' for b, t in items], n=cols)


# data
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
    # keyed on modification time so a fresh model-suite output is picked up without restarting
    return _read_results(p, p.stat().st_mtime) if p.exists() else None


@st.cache_data
def _read_results(path, mtime):
    return pd.read_csv(path)




panel, snap = load_data()
NAMES = snap.set_index("CountryCode").ShortName.to_dict()


def group_trend(var, by, min_share=0.3):
    g = panel.groupby([by, "Year"], observed=True)[var]
    size = panel.groupby(by, observed=True)["CountryCode"].nunique()
    out = pd.DataFrame({"median": g.median(), "n": g.count()}).reset_index()
    out = out[out["n"] / out[by].map(size).astype(float) >= min_share]
    return out


# story helpers (shared by the story pages)
def takeaway(headline, sub=""):
    """Action title: the section's conclusion as one sentence; wrap the anchor number in <em>."""
    st.markdown(f'<div class="takeaway">{headline}</div><div class="takeaway-sub">{sub}</div>', unsafe_allow_html=True)


def bridge(question):
    """Closing question that leads to the next part of the analysis."""
    st.markdown(f'<div class="bridge">{question}</div>', unsafe_allow_html=True)


def method_box(md, title="Method & preprocessing", styler=None):
    """Methodological details, folded away by default. `styler` adds a theme-aware table below the text."""
    with st.expander(title):
        st.markdown(md)
        if styler is not None:
            table(styler)


def country_picker(key, default_codes, label="Countries to highlight on every chart"):
    """Multiselect of country names; returns ISO codes in the order picked."""
    inv = {v: c for c, v in NAMES.items()}
    pick = st.multiselect(label, sorted(NAMES.values()), default=[NAMES[c] for c in default_codes if c in NAMES],
                          key=key)
    return [inv[n] for n in pick]


def highlight_colors(codes):
    """Vietnam red, the others from the palette, stable for a given selection."""
    others = iter(PALETTE * 3)
    return {c: VN_COLOR if c == VN else next(others) for c in codes}


def missing_results(*frames, cmd):
    """Warn and return True when precomputed story results are absent."""
    if any(f is None for f in frames):
        st.warning(f"Precomputed results are missing. Run section 10 of WDI_Analysis.ipynb (or `{cmd}`) first.")
        return True
    return False


# navigation
# Few top-level pages (Home · Data · Findings · Lab); each parent shows its children as a tab bar.
# app.py fills SECTIONS and PAGES. Only the selected tab is rendered (st.tabs would compute every child).
SECTIONS = {}  # parent key -> dict(title, icon, tabs=[(slug, label, render_fn), ...])
PAGES = {}     # parent key -> st.Page
ORDER = []     # reading order over every child: [(parent, slug), ...]


def goto(parent, slug=None):
    """Open a parent page (optionally on a given tab). Safe to call from the script body, not from callbacks."""
    if slug:
        st.session_state[f"_goto_{parent}"] = slug
    st.session_state["_scroll_top"] = st.session_state.get("_scroll_top", 0) + 1
    if st.session_state.get("_current_parent") == parent:
        st.rerun()
    st.switch_page(PAGES[parent])


def scroll_top():
    """After goto() (pager, landing cards) start the new tab at the top; Streamlit keeps the scroll position."""
    n = st.session_state.get("_scroll_top", 0)
    if n and st.session_state.get("_scrolled") != n:
        st.session_state["_scrolled"] = n
        import streamlit.components.v1 as components
        components.html(f"<script>/* {n} */ const d = window.parent.document;"
                        "(d.querySelector('[data-testid=stMain]') || d.querySelector('section.main'))?.scrollTo(0, 0);"
                        "window.parent.scrollTo(0, 0);</script>", height=0)


def _tab_bar(parent):
    tabs = SECTIONS[parent]["tabs"]
    slugs = [t[0] for t in tabs]
    key = f"tab_{parent}"
    wanted = st.session_state.pop(f"_goto_{parent}", None)
    if wanted in slugs:
        st.session_state[key] = wanted
    elif st.session_state.get(key) not in slugs:
        q = st.query_params.get("tab")
        last = st.session_state.get(f"_last_{parent}")
        st.session_state[key] = q if q in slugs else last if last in slugs else slugs[0]
    def keep_selected():  # clicking the active tab would deselect it; keep it selected instead
        if st.session_state.get(key) is None:
            st.session_state[key] = st.session_state.get(f"_last_{parent}") or slugs[0]

    sel = st.segmented_control(SECTIONS[parent]["title"], slugs, key=key, label_visibility="collapsed",
                               format_func=dict((t[0], t[1]) for t in tabs).get, width="stretch",
                               on_change=keep_selected)
    sel = sel or st.session_state.get(f"_last_{parent}") or slugs[0]
    st.session_state[f"_last_{parent}"] = sel
    st.query_params["tab"] = sel                                       # shareable link: /findings?tab=why
    return sel


def _pager(parent, slug):
    """Previous / next buttons along the reading order, across parents (B → Part 1, Part 3 → Lab)."""
    i = ORDER.index((parent, slug))
    label = {(p, s): (l if p == parent else f"{SECTIONS[p]['title']} · {l}")
             for p, sec in SECTIONS.items() for s, l, _ in sec["tabs"]}
    prev_, next_ = (ORDER[i - 1] if i > 0 else None), (ORDER[i + 1] if i + 1 < len(ORDER) else None)
    st.markdown('<div class="pager-rule"></div>', unsafe_allow_html=True)
    a, _, b = st.columns([2, 3, 2])
    target = None
    if prev_ is None:
        if a.button("← Home", key="pg_prev", type="tertiary"):
            target = ("home", None)
    elif a.button(f"← {label[prev_]}", key="pg_prev", type="tertiary"):
        target = prev_
    if next_ is not None and b.button(f"Next: {label[next_]} →", key="pg_next", width="stretch"):
        target = next_
    if target:
        goto(*target)


def section_page(parent):
    """Page function for a parent: tab bar, the selected child, then the pager."""
    def render():
        st.session_state["_current_parent"] = parent
        scroll_top()
        slug = _tab_bar(parent)
        fn = next(f for s, _, f in SECTIONS[parent]["tabs"] if s == slug)
        st.markdown('<div class="tab-body"></div>', unsafe_allow_html=True)
        fn()
        _pager(parent, slug)
    render.__name__ = f"page_{parent}"
    return render

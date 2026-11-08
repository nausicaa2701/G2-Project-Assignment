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

# ---------------------------------------------------------------- design system
# Minimal light and dark palettes: flat surfaces, hairline borders, one accent colour, Vietnam always in red.
# The toggle (top-right) stores its value in session state; app.py calls apply_theme() on every rerun.
MODES = {
    False: dict(bg="#ffffff", card="#ffffff", ink="#111827", grey="#6b7280", line="#e5e7eb", grid="#f3f4f6",
                field="#ffffff", blue="#2563eb", soft="#bfdbfe", shadow="rgba(0,0,0,0)", template="plotly_white"),
    True:  dict(bg="#0b0c0e", card="#111316", ink="#e5e7eb", grey="#9ca3af", line="#26292e", grid="#191b1f",
                field="#15171a", blue="#60a5fa", soft="#1e3a8a", shadow="rgba(0,0,0,0)", template="plotly_dark"),
}
FONT = 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue", Arial, sans-serif'
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
    INCOME_COLORS = dict(zip(INCOME_ORDER, ["#e4572e", "#f2a541", "#2a9d8f", BLUE]))
    CLUSTER_COLORS = ["#e4572e", "#f2a541", "#2a9d8f", BLUE, "#7c3aed", "#db2777", "#65a30d", GREY]
    PALETTE = [BLUE, "#f2a541", "#2a9d8f", "#e4572e", "#7c3aed", "#db2777", "#65a30d", "#a16207"]
    px.defaults.color_discrete_sequence = PALETTE
    c = C
    st.markdown(f"""<style>
    @import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap");
    html, body, [class*="css"], .stMarkdown, button, input, select, textarea {{ font-family: {FONT} !important; }}
    .block-container {{ padding: 2rem 1.5rem 3rem; max-width: 1180px; }}
    .stApp, header[data-testid="stHeader"] {{ background: {c["bg"]}; }}
    header[data-testid="stHeader"] {{ border-bottom: 1px solid {LINE}; }}
    h1, h2, h3 {{ color: {INK}; letter-spacing: -0.02em; }}
    footer, #MainMenu {{ visibility: hidden; }}

    /* page header (left-aligned) */
    .hero {{ padding: 1.6rem 0 1.4rem; border-bottom: 1px solid {LINE}; margin-bottom: .6rem; }}
    .hero .eyebrow {{ color: {GREY}; font-weight: 500; font-size: .85rem; margin-bottom: .5rem; }}
    .hero h1 {{ font-size: clamp(1.6rem, 3.2vw, 2.2rem); font-weight: 650; line-height: 1.2; margin: 0; padding: 0; }}
    .hero p {{ color: {GREY}; font-size: 1rem; line-height: 1.6; max-width: 720px; margin: .7rem 0 0; }}
    .hero [data-testid="stHeaderActionElements"] {{ display: none; }}

    /* section headings */
    .section-title {{ color: {INK}; font-size: 1.3rem; font-weight: 650; letter-spacing: -0.01em; margin: 2.2rem 0 .2rem; }}
    .section-sub {{ color: {GREY}; font-size: .95rem; margin-bottom: 1rem; }}
    .takeaway {{ color: {INK}; font-size: 1.15rem; font-weight: 600; line-height: 1.4; letter-spacing: -0.01em;
                 margin: 2.4rem 0 .3rem; }}
    .takeaway em {{ font-style: normal; color: {VN_COLOR}; }}
    .takeaway-sub {{ color: {GREY}; font-size: .93rem; line-height: 1.55; margin-bottom: 1rem; max-width: 900px; }}
    .bridge {{ color: {GREY}; font-size: .98rem; padding: .9rem 0 .2rem; margin-top: 2.6rem; border-top: 1px solid {LINE}; }}

    /* equal-height grids of tiles and cards (CSS grid, so every block in a row has the same height) */
    .grid {{ display: grid; gap: 12px; grid-template-columns: repeat(var(--n), minmax(0, 1fr)); margin: .4rem 0 1rem; }}
    @media (max-width: 900px) {{ .grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}
    @media (max-width: 520px) {{ .grid {{ grid-template-columns: 1fr; }} }}
    .tile, .insight, .card {{ background: {c["card"]}; border: 1px solid {LINE}; border-radius: 10px; padding: 16px 18px; }}
    .tile .k {{ color: {GREY}; font-size: .8rem; font-weight: 500; }}
    .tile .v {{ color: {INK}; font-size: 1.6rem; font-weight: 650; letter-spacing: -0.02em; line-height: 1.25; margin: .2rem 0; }}
    .tile .s {{ color: {GREY}; font-size: .8rem; line-height: 1.45; }}
    .insight b {{ display: block; color: {INK}; font-size: .98rem; font-weight: 600; margin-bottom: .3rem; }}
    .insight span {{ color: {GREY}; font-size: .9rem; line-height: 1.55; }}

    /* charts, tables, expanders: flat surfaces with a hairline border */
    div[data-testid="stPlotlyChart"] {{ background: {c["card"]}; border: 1px solid {LINE}; border-radius: 10px; padding: 6px; }}
    .tbl {{ background: {c["card"]}; border: 1px solid {LINE}; border-radius: 10px; overflow-x: auto; padding: 4px 12px; }}
    .tbl table {{ border-collapse: collapse; width: 100%; font-size: .86rem; color: {INK}; }}
    .tbl th {{ color: {GREY}; font-weight: 500; text-align: right; padding: .55rem .6rem; border-bottom: 1px solid {LINE}; }}
    .tbl th.row_heading {{ text-align: left; }}
    .tbl td {{ text-align: right; padding: .5rem .6rem; border-bottom: 1px solid {c["grid"]}; font-variant-numeric: tabular-nums; }}
    .tbl tr:last-child td {{ border-bottom: 0; }}
    [data-testid="stExpander"] details {{ background: {c["card"]}; border: 1px solid {LINE}; border-radius: 10px; }}
    [data-testid="stExpander"] summary, [data-testid="stExpander"] summary * {{ color: {INK} !important; }}
    [data-testid="stExpander"] summary:hover {{ background: {c["grid"]}; }}

    /* widgets */
    .st-key-dark {{ position: fixed; top: .8rem; right: 1.4rem; z-index: 1000001; width: auto !important; }}
    .stApp, .stMarkdown, [data-testid="stWidgetLabel"] p, [data-testid="stMarkdownContainer"] p, .st-key-dark p {{ color: {INK}; }}
    [data-testid="stWidgetLabel"] p {{ font-size: .85rem; color: {GREY} !important; }}
    [data-testid="stCaptionContainer"] {{ color: {GREY} !important; }}
    .stSelectbox [role="group"], .stMultiSelect [role="group"], .stTextInput input, .stNumberInput input,
    .stNumberInput button, div[data-baseweb="input"] {{ background: {c["field"]} !important; color: {INK} !important;
                border-color: {LINE} !important; }}
    div[data-baseweb="select"] > div, .stNumberInput input {{ border-radius: 8px !important; }}
    [role="combobox"], .stSelectbox svg, .stMultiSelect svg, .stNumberInput svg {{ color: {INK} !important; }}
    [data-testid="stSelectboxVirtualDropdown"], [role="listbox"] {{ background: {c["card"]} !important; color: {INK} !important;
                border-color: {LINE} !important; }}
    [role="option"] {{ color: {INK} !important; }}
    [role="option"]:hover, [role="option"][data-focused="true"] {{ background: {c["grid"]} !important; }}
    [data-tag] {{ background: {c["grid"]} !important; color: {INK} !important; border: 1px solid {LINE}; }}
    [data-tag] * {{ color: {INK} !important; }}
    [data-testid="stSliderThumbValue"], [data-testid="stSliderTickBarMin"], [data-testid="stSliderTickBarMax"] {{ color: {GREY}; }}
    [data-testid="stForm"] {{ border: 1px solid {LINE}; background: {c["card"]}; border-radius: 10px; }}
    [data-testid="stAlert"] {{ background: {c["card"]}; color: {INK}; border: 1px solid {LINE}; border-radius: 10px; }}
    button[data-variant="segmented_control"] {{ background: {c["field"]}; color: {INK}; border-color: {LINE}; }}
    button[data-variant="segmented_control"][data-selected="true"], button[data-variant="segmented_control"][aria-checked="true"]
        {{ background: {INK}; color: {c["bg"]}; border-color: {INK}; }}
    [data-testid="stTopNavLinkContainer"] span, header a span {{ color: {INK} !important; }}
    [data-testid="stTooltipIcon"] svg {{ color: {GREY}; }}
    .stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {{ background: {INK}; color: {c["bg"]};
                border: 1px solid {INK}; border-radius: 8px; padding: .5rem 1.1rem; font-weight: 500; box-shadow: none; }}
    .stButton > button:hover, .stFormSubmitButton > button:hover {{ opacity: .85; color: {c["bg"]}; }}
    .stButton > button p, .stDownloadButton > button p, .stFormSubmitButton > button p {{ color: inherit !important; }}
    .stButton > button[data-testid="stBaseButton-secondary"] {{ background: transparent; color: {INK}; border-color: {LINE}; }}
    .stButton > button[data-testid="stBaseButton-tertiary"] {{ background: transparent; color: {BLUE}; border: 0; padding: .2rem 0; }}
    .stButton > button[data-testid="stBaseButton-tertiary"]:hover {{ color: {INK}; opacity: 1; }}

    /* tab bar of a parent page (segmented control restyled as underlined tabs) */
    [class*="st-key-tab_"] {{ border-bottom: 1px solid {LINE}; position: sticky; top: 3.6rem; z-index: 999; background: {c["bg"]}; }}
    [class*="st-key-tab_"] [data-testid="stButtonGroup"], [class*="st-key-tab_"] [role="radiogroup"] {{ gap: .25rem; }}
    [class*="st-key-tab_"] button {{ background: transparent !important; border: 0 !important; border-radius: 0 !important;
                 color: {GREY} !important; padding: .75rem .9rem !important; border-bottom: 2px solid transparent !important;
                 box-shadow: none !important; flex: 0 1 auto !important; }}
    [class*="st-key-tab_"] button:hover {{ color: {INK} !important; }}
    [class*="st-key-tab_"] button[aria-checked="true"], [class*="st-key-tab_"] button[data-selected="true"],
    [class*="st-key-tab_"] button[kind="segmented_controlActive"] {{ color: {INK} !important; background: transparent !important;
                 border-bottom: 2px solid {INK} !important; }}
    [class*="st-key-tab_"] p {{ color: inherit !important; font-size: .95rem !important; font-weight: 500; }}
    iframe[height="0"] {{ display: block; }}
    .element-container:has(> iframe[height="0"]), .stElementContainer:has(> iframe[height="0"]) {{ display: none; }}
    .pager-rule {{ border-top: 1px solid {LINE}; margin: 2.6rem 0 .8rem; }}

    /* landing page */
    .home-head {{ padding: 2.2rem 0 1.6rem; border-bottom: 1px solid {LINE}; }}
    .home-head .eyebrow {{ color: {GREY}; font-size: .85rem; font-weight: 500; }}
    .home-head h1 {{ font-size: clamp(2rem, 4.5vw, 2.9rem); font-weight: 700; line-height: 1.1; letter-spacing: -0.03em;
                    margin: .6rem 0 .5rem; padding: 0; color: {INK}; }}
    .home-head .sub {{ color: {GREY}; font-size: 1.05rem; }}
    .home-head [data-testid="stHeaderActionElements"] {{ display: none; }}
    .meta {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; margin: 1.4rem 0 .4rem; }}
    @media (max-width: 760px) {{ .meta {{ grid-template-columns: 1fr; }} }}
    .meta .card .k {{ color: {GREY}; font-size: .78rem; font-weight: 500; text-transform: uppercase; letter-spacing: .04em; }}
    .meta .card .v {{ color: {INK}; font-size: .93rem; line-height: 1.6; margin-top: .35rem; }}
    .tldr {{ border: 1px solid {LINE}; border-radius: 10px; padding: 18px 22px; margin: .8rem 0 0; background: {c["card"]}; }}
    .tldr h3 {{ font-size: .78rem; font-weight: 600; color: {GREY}; text-transform: uppercase; letter-spacing: .06em;
               margin: 0 0 .6rem; padding: 0; }}
    .tldr ul {{ margin: 0; padding-left: 1.1rem; }}
    .tldr li {{ color: {INK}; font-size: .97rem; line-height: 1.6; margin: .25rem 0; }}
    .tldr li b {{ font-weight: 600; }}
    .tldr li em {{ font-style: normal; color: {VN_COLOR}; font-weight: 600; }}
    .card .t {{ color: {INK}; font-weight: 600; font-size: 1rem; }}
    .card .d {{ color: {GREY}; font-size: .88rem; line-height: 1.5; margin-top: .3rem; }}
    .footer {{ color: {GREY}; font-size: .82rem; padding: 1.2rem 0 .4rem; border-top: 1px solid {LINE}; margin-top: 2.6rem; line-height: 1.7; }}
    </style>""", unsafe_allow_html=True)


def style(fig, h=420, legend=True):
    fig.update_layout(template=C["template"], height=h, font=dict(family=FONT, color=INK, size=12),
                      margin=dict(l=8, r=8, t=44, b=8), paper_bgcolor=C["card"], plot_bgcolor=C["card"],
                      title=dict(x=0.01, xanchor="left", font=dict(size=14, weight=600)), colorway=PALETTE,
                      showlegend=legend, legend=dict(orientation="h", y=-0.16, title=None, font=dict(size=11)),
                      hoverlabel=dict(font_family=FONT, bgcolor=C["card"], font_color=INK))
    fig.update_xaxes(showgrid=False, linecolor=LINE, ticks="", title_font=dict(size=11, color=GREY))
    fig.update_yaxes(gridcolor=C["grid"], zeroline=False, linecolor=LINE, title_font=dict(size=11, color=GREY))
    if any(t.type == "choropleth" for t in fig.data):
        fig.update_geos(bgcolor=C["card"], landcolor=C["grid"], showland=True, lakecolor=C["card"])
    return fig


def hero(eyebrow, title, sub):
    """Left-aligned page header: small label, title, one-line summary."""
    st.markdown(f'<div class="hero"><div class="eyebrow">{eyebrow}</div><h1>{title.replace("<br>", " ")}</h1>'
                f'<p>{sub}</p></div>', unsafe_allow_html=True)


def section(title, sub=""):
    st.markdown(f'<div class="section-title">{title}</div>' + (f'<div class="section-sub">{sub}</div>' if sub else ""),
                unsafe_allow_html=True)


def table(styler):
    """Theme-aware HTML table from a pandas Styler; text columns are left-aligned, numbers right-aligned."""
    df = styler.data
    text = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])]
    if text:
        styler = styler.set_properties(subset=text, **{"text-align": "left"})
        styler = styler.set_table_styles([{"selector": f"th.col{list(df.columns).index(c)}",
                                           "props": "text-align: left"} for c in text], overwrite=False)
    st.markdown(f'<div class="tbl">{styler.to_html()}</div>', unsafe_allow_html=True)


def grid(blocks, n=None):
    """Equal-width, equal-height blocks in one row (wraps to two columns on tablets, one on phones)."""
    n = n or len(blocks)
    st.markdown(f'<div class="grid" style="--n:{n}">{"".join(blocks)}</div>', unsafe_allow_html=True)


def tiles(items):
    grid([f'<div class="tile"><div class="k">{k}</div><div class="v">{v}</div><div class="s">{s}</div></div>'
          for k, v, s in items])


def chart(fig, h=420, legend=True, target=st):
    """style() + st.plotly_chart with the app defaults; `target` can be a column."""
    target.plotly_chart(style(fig, h, legend), width="stretch", theme=None)


def insights(items, cols=2):
    """Cards with a bold lead and a sentence, in an equal-height grid."""
    grid([f'<div class="insight"><b>{b}</b><span>{t}</span></div>' for b, t in items], n=cols)


# ---------------------------------------------------------------- data
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


# ---------------------------------------------------------------- story helpers (shared by the story pages)
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


# ---------------------------------------------------------------- navigation
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

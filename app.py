"""World Development Indicators: home page, data exploration and preprocessing, the three-part analysis
and a model lab.

Run: streamlit run app.py

Four top-level pages; each parent shows its children as tabs (only the open tab is computed):
    Home       ui/landing.py   title, group, TL;DR of the findings, links
    Data       ui/data.py      A · Exploration, B · Preprocessing
    Findings   ui/part1.py     1 · What
               ui/part2.py     2 · Why
               ui/part3.py     3 · So what
    Lab        ui/explore.py   trends, compare, models, clusters (free exploration)
ui/core.py holds the design system, data loading, story helpers and the tab navigation.
"""
import streamlit as st

st.set_page_config(page_title="Does richer mean more developed? · G2", page_icon="🌍", layout="wide")

from ui import core  # noqa: E402  (after set_page_config: core loads cached data)
from ui import landing  # noqa: E402
from ui.sections import sections  # noqa: E402

core.apply_theme()
core.SECTIONS = sections()
core.ORDER = [(p, s) for p, sec in core.SECTIONS.items() for s, _, _ in sec["tabs"]]
core.PAGES = {"home": st.Page(landing.page, title="Home", icon=":material/home:", url_path="home", default=True)}
core.PAGES |= {p: st.Page(core.section_page(p), title=sec["title"], icon=sec["icon"], url_path=p)
               for p, sec in core.SECTIONS.items()}
st.session_state["_current_parent"] = None   # set again by the parent page that runs
nav = st.navigation(list(core.PAGES.values()), position="top")
st.toggle("Dark mode", key="dark")
nav.run()

"""Streamlit app for the WDI study. Run: streamlit run app.py

Pages (each parent shows its children as tabs; only the open tab is computed):
    Home       ui/landing.py
    Data       ui/data.py       A · Exploration, B · Preprocessing
    Findings   ui/part1-3.py    1 · What changed, 2 · Why, 3 · So what
    Lab        ui/explore.py    Trends, Compare, Models, Clusters
"""
import streamlit as st

st.set_page_config(page_title="Does richer mean more developed? · G2", page_icon="🌍", layout="wide")

from ui import core
from ui import landing
from ui.sections import sections

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

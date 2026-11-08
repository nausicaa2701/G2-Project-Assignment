"""Every page and tab of the app renders without an exception: run with `python tests/test_app.py` (about 1 min).

Tabs are rendered through their parent page (tab bar, the selected child, pager), selected by the ?tab= query
parameter exactly like a shared link.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from streamlit.testing.v1 import AppTest

from ui.sections import sections

LANDING = """
import sys
sys.path.insert(0, {root!r})
from ui import core, landing
core.apply_theme()
landing.page()
"""
PARENT = """
import sys
sys.path.insert(0, {root!r})
from ui import core
from ui.sections import sections
core.apply_theme()
core.SECTIONS = sections()
core.ORDER = [(p, s) for p, sec in core.SECTIONS.items() for s, _, _ in sec["tabs"]]
core.section_page({parent!r})()
"""


def check(at, name):
    assert not at.exception, (name, at.exception)
    assert not at.warning, (name, [w.value for w in at.warning])


for dark in (False, True):
    mode = "dark " if dark else "light"
    at = AppTest.from_string(LANDING.format(root=str(ROOT)), default_timeout=300)
    at.session_state["dark"] = dark
    check(at.run(), ("landing", dark))
    print(f"ok  {mode}  report")
    for parent, sec in sections().items():
        for slug, label, _ in sec["tabs"]:
            at = AppTest.from_string(PARENT.format(root=str(ROOT), parent=parent), default_timeout=300)
            at.session_state["dark"] = dark
            at.query_params["tab"] = slug
            check(at.run(), (parent, slug, dark))
            assert at.session_state[f"tab_{parent}"] == slug, (parent, slug)
            print(f"ok  {mode}  {parent}?tab={slug}")

# the real entry point (navigation + default page)
at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=300).run()
assert not at.exception, at.exception
print("ok  app.py")

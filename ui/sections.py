"""The parent pages and their tabs (Data · Findings · Lab), shared by app.py and tests/test_app.py."""
from ui import data, explore, part1, part2, part3


def sections():
    """parent key -> dict(title, icon, tabs=[(slug, tab label, page function), ...]) in reading order."""
    return {
        "data": dict(title="Data", icon=":material/dataset:", tabs=[
            ("exploration", "A · Exploration", data.page_a),
            ("preprocessing", "B · Preprocessing", data.page_b)]),
        "findings": dict(title="Findings", icon=":material/insights:", tabs=[
            ("what", "1 · What changed", part1.page),
            ("why", "2 · Why", part2.page),
            ("so-what", "3 · So what", part3.page)]),
        "lab": dict(title="Lab", icon=":material/science:", tabs=[
            ("trends", "Trends", explore.page_trends),
            ("compare", "Compare", explore.page_compare),
            ("models", "Models", explore.page_models),
            ("clusters", "Clusters", explore.page_clusters)]),
    }

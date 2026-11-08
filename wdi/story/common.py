"""Shared constants and loaders for the experiments (wdi/story/*)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from wdi.models import ROOT, data_path

OUT, FIG = ROOT / "results" / "story", ROOT / "figures" / "story"
VN, VN_COLOR, GREY = "VNM", "#c0392b", "#9aa0a6"
PEERS = ["CHN", "THA", "IDN", "PHL", "MYS"]
INCOME_ORDER = ["Low income", "Lower middle income", "Upper middle income", "High income"]
META = ["CountryCode", "ShortName", "Region", "Income"]

# Same 15 indicators and preprocessing as the Clusters page of the app.
CLUSTER_VARS = ["gdp_pc", "life_exp", "u5_mort", "fertility", "urban", "age65", "enrol_secondary", "internet",
                "mobile", "electricity", "co2_pc", "energy_pc", "safe_water", "forest", "trade_open"]
CLUSTER_LOG = ["gdp_pc", "u5_mort", "co2_pc", "energy_pc", "trade_open"]
CLUSTER_NAMES = {1: "Low development", 2: "Transition", 3: "Emerging", 4: "Advanced"}
# Social outcomes only (no income, no energy/CO2) for the "development twins" of E3.2.
SOCIAL_VARS = ["life_exp", "u5_mort", "fertility", "age65", "enrol_secondary", "internet", "mobile",
               "electricity", "safe_water", "urban"]


def panel():
    return pd.read_csv(data_path("wdi_panel_wide.csv"))


def snapshot():
    return pd.read_csv(data_path("wdi_snapshot_2005_2014.csv"))


def numeric(df):
    """The indicator columns of the panel or snapshot (everything but keys and metadata)."""
    return df.drop(columns=[c for c in META + ["Year"] if c in df])


def wcv(x, w=None):
    """Coefficient of variation std/mean, optionally weighted (population-weighted inequality)."""
    w = np.ones_like(x) if w is None else w
    m = np.average(x, weights=w)
    return np.sqrt(np.average((x - m) ** 2, weights=w)) / m


def _save(fig, name):
    FIG.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(FIG / name, dpi=150)
    plt.close(fig)

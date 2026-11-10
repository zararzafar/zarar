"""Shared access to the NVE Magasinstatistikk API (replaces the CSV file from part 1).

API documentation: https://biapi.nve.no/magasinstatistikk/swagger
The endpoint HentOffentligData returns all weekly observations for all areas in one request
(it has no date parameters), so the selected interval is applied right after the download.
The download is cached per interval, so moving the slider back to an earlier choice is instant.
"""
import pandas as pd
import requests
import streamlit as st

BASE_URL = "https://biapi.nve.no/magasinstatistikk/api/Magasinstatistikk"

# Norwegian -> English column names (same mapping as in part 1)
COLUMN_NAMES = {
    "dato_Id": "date",
    "omrType": "area_type",
    "omrnr": "area_number",
    "iso_aar": "iso_year",
    "iso_uke": "iso_week",
    "fyllingsgrad": "fill_rate",
    "kapasitet_TWh": "capacity_TWh",
    "fylling_TWh": "stored_energy_TWh",
    "neste_Publiseringsdato": "next_publication_date",
    "fyllingsgrad_forrige_uke": "fill_rate_previous_week",
    "endring_fyllingsgrad": "fill_rate_change",
}

VALUE_COLUMNS = ["fill_rate", "capacity_TWh", "stored_energy_TWh",
                 "fill_rate_previous_week", "fill_rate_change"]

LABELS = {
    "fill_rate": "Fill rate (share of capacity)",
    "capacity_TWh": "Reservoir capacity (TWh)",
    "stored_energy_TWh": "Stored energy (TWh)",
    "fill_rate_previous_week": "Fill rate previous week (share)",
    "fill_rate_change": "Weekly change in fill rate",
}

AREA_TYPES = {"NO": "Norway (whole country)", "EL": "Price areas (NO1-NO5)",
              "VASS": "Water-course areas (VASS1-VASS4)"}

# First month with data in the API; used to build the month slider without downloading
FIRST_MONTH = pd.Period("1995-01", freq="M")


def month_options() -> list[str]:
    """All months from January 1995 to the current month, as 'YYYY-MM' strings."""
    now = pd.Timestamp.now().to_period("M")
    return [str(p) for p in pd.period_range(FIRST_MONTH, now, freq="M")]


@st.cache_data(ttl=24 * 3600, show_spinner="Downloading area names from NVE ...")
def area_names() -> dict:
    """Map (area_type, area_number) -> short name, e.g. ('EL', 1) -> 'NO 1'."""
    data = requests.get(f"{BASE_URL}/HentOmråder", timeout=30).json()[0]
    names = {}
    for group in data.values():          # 'land', 'elspot' and 'vassdrag'
        for area in group:
            names[(area["omrType"], area["omrnr"])] = area["navn"]
    return names


@st.cache_data(ttl=6 * 3600, show_spinner="Downloading reservoir data from NVE ...")
def download(start_month: str, end_month: str) -> pd.DataFrame:
    """Download weekly reservoir data and keep only the weeks inside [start_month, end_month]."""
    response = requests.get(f"{BASE_URL}/HentOffentligData", timeout=60)
    response.raise_for_status()
    df = pd.DataFrame(response.json()).rename(columns=COLUMN_NAMES)
    df["date"] = pd.to_datetime(df["date"])
    # As in part 1: the rows are not sorted, so sort by area and date
    df = df.sort_values(["area_type", "area_number", "date"]).reset_index(drop=True)
    df["month"] = df["date"].dt.strftime("%Y-%m")
    df = df[(df["month"] >= start_month) & (df["month"] <= end_month)]
    # Readable area label, e.g. 'NO 1' or 'VASS2'
    names = area_names()
    df["area"] = [names.get((t, n), f"{t}{n}") for t, n in zip(df["area_type"], df["area_number"])]
    return df


def _remember(key: str, default):
    """Keep a widget value when the user moves between pages.

    Streamlit forgets the state of widgets that are not shown on the current page, so the value is
    copied to a separate session_state key that is not tied to a widget.
    """
    if key not in st.session_state:
        st.session_state[key] = default
    st.session_state["_w_" + key] = st.session_state[key]


def _store(key: str):
    st.session_state[key] = st.session_state["_w_" + key]


def controls(with_column: bool = False):
    """Sidebar controls shared by the reservoir pages. Returns (start, end, area_type, column)."""
    months = month_options()
    _remember("interval", (months[-12], months[-1]))   # default: the last 12 months
    _remember("area_type", "EL")
    _remember("column", "fill_rate")

    with st.sidebar:
        st.header("Reservoir data")
        start, end = st.select_slider("Months to download", options=months,
                                      key="_w_interval", on_change=_store, args=("interval",))
        area_type = st.radio("Type of areas", options=list(AREA_TYPES),
                             format_func=lambda t: AREA_TYPES[t],
                             key="_w_area_type", on_change=_store, args=("area_type",))
        column = st.selectbox("Value to show", options=VALUE_COLUMNS, format_func=LABELS.get,
                              key="_w_column", on_change=_store, args=("column",))
    return start, end, area_type, column

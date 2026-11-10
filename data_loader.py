"""Shared data loading for all pages of the Streamlit app.

The same cleaning steps as in the Jupyter Notebook (IND320_part1.ipynb) are used:
rename the Norwegian headers to English, keep the national total for Norway and sort by date.
In part 2 of the project this file will be changed to read from MongoDB instead of the CSV file.
"""
import pandas as pd
import streamlit as st

DATA_PATH = "data/reservoirs.csv"

# Norwegian -> English column names (same mapping as in the notebook)
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

# The numeric measurement columns shown in the app
VALUE_COLUMNS = ["fill_rate", "capacity_TWh", "stored_energy_TWh",
                 "fill_rate_previous_week", "fill_rate_change"]

# Readable labels used in tables and plots
LABELS = {
    "fill_rate": "Fill rate (share of capacity)",
    "capacity_TWh": "Reservoir capacity (TWh)",
    "stored_energy_TWh": "Stored energy (TWh)",
    "fill_rate_previous_week": "Fill rate previous week (share)",
    "fill_rate_change": "Weekly change in fill rate",
}


@st.cache_data  # the CSV is only read once; later reruns reuse the cached result
def load_data() -> pd.DataFrame:
    """Read the CSV, rename columns and return the national weekly series for Norway."""
    raw = pd.read_csv(DATA_PATH, parse_dates=["dato_Id"])
    df = raw.rename(columns=COLUMN_NAMES)
    norway = (df[df["area_type"] == "NO"]       # national total only
              .sort_values("date")              # the raw file is not sorted
              .reset_index(drop=True))
    # Year-month label used by the month slider and the first-month table
    norway["month"] = norway["date"].dt.strftime("%Y-%m")
    return norway[["date", "month"] + VALUE_COLUMNS]

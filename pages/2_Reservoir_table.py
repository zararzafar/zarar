"""Page 2: one row per area of the chosen type, with a LineChartColumn of the chosen value."""
import pandas as pd
import streamlit as st

from nve_api import AREA_TYPES, LABELS, controls, download

st.set_page_config(page_title="IND320 – Reservoir table", page_icon="📋", layout="wide")
st.title("Reservoir table")

start, end, area_type, column = controls()
df = download(start, end)                       # cached download from the NVE API
data = df[df["area_type"] == area_type]

if data.empty:
    st.warning("No data in the chosen period.")
    st.stop()

st.write(f"**{AREA_TYPES[area_type]}**, {start} to {end}: one row per area. "
         f"The chart shows the weekly values of *{LABELS[column].lower()}*.")

# One row per area number. The weekly values are stored as a list, which
# LineChartColumn draws as a small line chart inside the table cell.
rows = []
for area, group in data.groupby("area", sort=True):
    rows.append({
        "Area": area,
        "Weeks": len(group),
        "Latest": round(group[column].iloc[-1], 3),
        "Mean": round(group[column].mean(), 3),
        "Weekly values": group[column].round(4).tolist(),
    })
table = pd.DataFrame(rows)

st.dataframe(
    table,
    hide_index=True,
    use_container_width=True,
    column_config={
        "Weekly values": st.column_config.LineChartColumn(
            f"{LABELS[column]} ({start} to {end})", width="large"),
    },
)

with st.expander("Show the downloaded rows"):
    st.dataframe(data[["date", "area", "iso_year", "iso_week", column]],
                 hide_index=True, use_container_width=True)

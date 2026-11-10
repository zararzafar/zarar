"""Page 3: line plot with one line for each area of the chosen area type."""
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import streamlit as st

from nve_api import AREA_TYPES, LABELS, controls, download

st.set_page_config(page_title="IND320 – Reservoir plot", page_icon="📈", layout="wide")
st.title("Reservoir plot")

start, end, area_type, column = controls()
df = download(start, end)
data = df[df["area_type"] == area_type]

if data.empty:
    st.warning("No data in the chosen period.")
    st.stop()

fig, ax = plt.subplots(figsize=(11, 4.8))
for area, group in data.groupby("area", sort=True):   # one line per area number
    ax.plot(group["date"], group[column], marker="o", markersize=2.5, linewidth=1.3, label=area)

period = start if start == end else f"{start} to {end}"
ax.set_title(f"{LABELS[column]} – {AREA_TYPES[area_type]}, {period}")
ax.set_xlabel("Date")
ax.set_ylabel(LABELS[column])
ax.grid(alpha=0.3)
ax.legend(title="Area", fontsize=8, loc="best")
ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))
fig.tight_layout()
st.pyplot(fig)

st.caption(f"{data['date'].nunique()} weeks shown. Source: NVE Magasinstatistikk API (weekly values).")

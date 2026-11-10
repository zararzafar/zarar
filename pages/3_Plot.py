"""Page 3: plot of the imported data with column selection and month range selection."""
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import streamlit as st

from data_loader import LABELS, VALUE_COLUMNS, load_data

st.set_page_config(page_title="IND320 – Plot", page_icon="📈", layout="wide")
st.title("Plot of the reservoir data")

df = load_data()
ALL = "All columns"

# Drop-down menu: one single column, or all columns together
choice = st.selectbox(
    "Choose a column",
    options=[ALL] + VALUE_COLUMNS,
    format_func=lambda c: c if c == ALL else LABELS[c],
)

# Selection slider over the months; default is the first month only
months = df["month"].unique().tolist()
start, end = st.select_slider(
    "Choose a range of months",
    options=months,
    value=(months[0], months[0]),
)
subset = df[(df["month"] >= start) & (df["month"] <= end)]

fig, ax = plt.subplots(figsize=(10, 4.5))
if choice == ALL:
    # The columns have very different scales (fractions vs. TWh), so each column is
    # min-max scaled using its minimum and maximum over the whole data set.
    for col in VALUE_COLUMNS:
        lo, hi = df[col].min(), df[col].max()
        # A constant column (capacity) has hi == lo; draw it at 0.5 to avoid dividing by zero
        scaled = (subset[col] - lo) / (hi - lo) if hi > lo else subset[col] * 0 + 0.5
        ax.plot(subset["date"], scaled, marker="o", markersize=3, label=LABELS[col])
    ax.set_ylabel("Scaled value (0 = min, 1 = max of full data)")
    ax.legend(fontsize=8, loc="best")
    title = "All columns (min-max scaled)"
else:
    ax.plot(subset["date"], subset[choice], marker="o", markersize=3, color="tab:blue")
    ax.set_ylabel(LABELS[choice])
    title = LABELS[choice]

period = start if start == end else f"{start} to {end}"
ax.set_title(f"{title}, {period}")
ax.set_xlabel("Date")
ax.grid(alpha=0.3)
ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))
fig.tight_layout()
st.pyplot(fig)

st.caption(f"{len(subset)} weekly observations shown. Data: NVE reservoir statistics, national total.")

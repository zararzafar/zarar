"""Page 2: table with one row per data column and a line chart of the first month."""
import pandas as pd
import streamlit as st

from data_loader import LABELS, VALUE_COLUMNS, load_data

st.set_page_config(page_title="IND320 – Data table", page_icon="📋", layout="wide")
st.title("Data table")

df = load_data()

# The first month in the data set (e.g. "1995-01") and its weekly rows
first_month = df["month"].iloc[0]
first = df[df["month"] == first_month]

st.write(f"Each row is one column of the imported data. The chart shows the weekly values "
         f"in the first month of the data series (**{first_month}**, {len(first)} weeks).")

# Build the table: one row per column, with the first-month values stored as a list
table = pd.DataFrame({
    "Column": VALUE_COLUMNS,
    "Description": [LABELS[c] for c in VALUE_COLUMNS],
    "First month": [first[c].round(4).tolist() for c in VALUE_COLUMNS],
})

st.dataframe(
    table,
    hide_index=True,
    use_container_width=True,
    column_config={
        # LineChartColumn draws the list in each cell as a small line chart (row-wise)
        "First month": st.column_config.LineChartColumn(
            f"First month ({first_month})",
            help="Weekly values in the first month of the data",
            width="large",
        ),
    },
)

# Also show the underlying numbers for the first month
with st.expander("Show the raw values for the first month"):
    st.dataframe(first.set_index("date")[VALUE_COLUMNS], use_container_width=True)

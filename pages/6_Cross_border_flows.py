"""Page 6: cross-border electricity flows to/from Norway, read from MongoDB.

Left column: radio buttons for the connection + year selector -> pie chart of import vs. export.
Right column: pills for the months -> line plot of daily flows in each direction.
"""
import calendar

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import streamlit as st

from mongo_data import load_flows

st.set_page_config(page_title="IND320 – Cross-border flows", page_icon="🔌", layout="wide")
st.title("Cross-border electricity flows")

try:
    flows = load_flows()
except Exception:            # no MongoDB secret yet, or the collection is still empty
    st.info("The cross-border flow data are not available yet: they are loaded into MongoDB from the "
            "Jupyter Notebook as soon as the ENTSO-E API token has been approved.")
    st.stop()
connections = sorted(flows["connection"].unique())
COLORS = {"export": "tab:orange", "import": "tab:blue"}

left, right = st.columns(2)

with left:
    st.subheader("Yearly import and export")
    connection = st.radio("Connection", connections, horizontal=True)
    years = sorted(flows["date"].dt.year.unique())
    year = st.selectbox("Year", years, index=len(years) - 1)

    sel = flows[(flows["connection"] == connection) & (flows["date"].dt.year == year)]
    totals = sel.groupby("direction")["energy_mwh"].sum() / 1000      # MWh -> GWh
    totals = totals[totals > 0]

    if totals.empty:
        st.info("No flow data for this connection and year.")
    else:
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.pie(totals, labels=[f"{d.capitalize()}\n{v:,.0f} GWh" for d, v in totals.items()],
               colors=[COLORS[d] for d in totals.index], autopct="%1.0f%%", startangle=90)
        ax.set_title(f"{connection}, {year}")
        st.pyplot(fig)
        days = sel["date"].dt.date.nunique()
        if days < 365:
            st.caption(f"Note: only {days} days of data in {year} (data cover the last two years).")

with right:
    st.subheader("Daily flows for chosen months")
    month_names = list(calendar.month_abbr)[1:]
    chosen = st.pills("Months", month_names, selection_mode="multi", default=[month_names[0]])

    month_numbers = [month_names.index(m) + 1 for m in (chosen or [])]
    sel = flows[(flows["connection"] == connection) & (flows["date"].dt.year == year)
                & (flows["date"].dt.month.isin(month_numbers))]

    if sel.empty:
        st.info("Choose at least one month with data.")
    else:
        fig, ax = plt.subplots(figsize=(7, 4.3))
        for direction, group in sel.groupby("direction"):
            ax.plot(group["date"], group["energy_mwh"] / 1000, marker="o", markersize=2.5,
                    color=COLORS.get(direction), label=direction.capitalize())
        ax.set_title(f"{connection}, {year}: daily flow")
        ax.set_xlabel("Date")
        ax.set_ylabel("Energy per day (GWh)")
        ax.grid(alpha=0.3)
        ax.legend()
        ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))
        fig.tight_layout()
        st.pyplot(fig)
        st.caption("Export = from Norway to the neighbouring area, import = into Norway.")

with st.expander("About the data on this page"):
    st.markdown(
        "- **Source:** ENTSO-E Transparency Platform, *Cross-border physical flows* "
        "(document type A11), retrieved with the `entsoe-py` package for the last two years.\n"
        "- **Processing:** in the Jupyter Notebook the hourly flows were stored in a local "
        "Cassandra database with Spark, then Spark extracted the relevant columns and summed them "
        "to daily energy (MWh) per connection and direction.\n"
        "- **Storage:** the daily values were inserted into MongoDB (database `ind320`, collection "
        "`crossborder_daily`), which this page reads directly.\n"
        "- **Connections:** Norwegian bidding zones (NO1-NO5) to neighbouring zones in Sweden, "
        "Finland, Denmark, Germany, the Netherlands and Great Britain."
    )

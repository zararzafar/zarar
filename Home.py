"""Front page of the IND320 Streamlit app.

Run locally with:  streamlit run Home.py
Every file in the pages/ folder becomes a page in the sidebar menu.
"""
import streamlit as st

st.set_page_config(page_title="IND320 – Home", page_icon="💧", layout="wide")

st.title("IND320 – Data to decision")
st.subheader("Norwegian hydropower reservoirs and cross-border electricity flows")

st.write(
    "This app is the online part of my IND320 project work. Since part 2, the reservoir data "
    "are downloaded directly from the NVE Magasinstatistikk API, and the cross-border electricity "
    "flows (from ENTSO-E, prepared with Cassandra and Spark) are read from a MongoDB database."
)
st.write("Use the menu in the sidebar to move between the pages:")
st.markdown(
    "- **Reservoir table** – one row per area, with a line chart of the chosen value\n"
    "- **Reservoir plot** – lines for each area in the chosen area type and period\n"
    "- **Cross-border flows** – yearly import/export and daily flows for Norway's connections\n"
    "- **About** – data sources and notes"
)
st.info("On the reservoir pages, the slider in the sidebar decides which months are downloaded "
        "from NVE, and the radio buttons choose between Norway, price areas and water-course areas.")

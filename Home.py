"""Front page of the IND320 Streamlit app.

Run locally with:  streamlit run Home.py
Streamlit automatically turns every file in the pages/ folder into a page and lists all pages
in the sidebar menu, which is used for navigation between the four pages.
"""
import streamlit as st

from data_loader import load_data

st.set_page_config(page_title="IND320 – Home", page_icon="💧", layout="wide")

st.title("IND320 – Data to decision")
st.subheader("Norwegian hydropower reservoirs")

st.write(
    "This app is the online part of my IND320 project work. "
    "In part 1 the data comes from a local CSV file (`reservoirs.csv`) with weekly "
    "reservoir statistics for Norway from 1995 to 2026."
)
st.write("Use the menu in the sidebar to move between the pages:")
st.markdown(
    "- **Data table** – one row per data column, with a mini chart of the first month\n"
    "- **Plot** – interactive plot with column and month selection\n"
    "- **About** – placeholder page for later parts of the project"
)

# Load (and cache) the data here as well, so the other pages open quickly
df = load_data()
st.caption(f"Loaded {len(df)} weekly observations from "
           f"{df['date'].min():%d.%m.%Y} to {df['date'].max():%d.%m.%Y}.")

# Extra navigation links in the sidebar (in addition to the automatic page list)
with st.sidebar:
    st.header("Navigation")
    st.page_link("Home.py", label="Home", icon="🏠")
    st.page_link("pages/2_Data_table.py", label="Data table", icon="📋")
    st.page_link("pages/3_Plot.py", label="Plot", icon="📈")
    st.page_link("pages/4_About.py", label="About", icon="ℹ️")

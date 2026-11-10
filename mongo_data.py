"""Read the cross-border flow data that the Jupyter Notebook stored in MongoDB.

The connection string is read from Streamlit secrets:
- locally from .streamlit/secrets.toml (this file is in .gitignore and never pushed to GitHub)
- on streamlit.app from the app's "Secrets" settings
    [mongo]
    uri = "mongodb+srv://<user>:<password>@<cluster>/..."
"""
import pandas as pd
import pymongo
import streamlit as st

DB_NAME = "ind320"
COLLECTION = "crossborder_daily"


@st.cache_resource  # one client for the whole app
def client() -> pymongo.MongoClient:
    return pymongo.MongoClient(st.secrets["mongo"]["uri"])


@st.cache_data(ttl=600, show_spinner="Reading cross-border flows from MongoDB ...")
def load_flows() -> pd.DataFrame:
    """Daily energy (MWh) per connection and direction, as prepared with Spark in the notebook."""
    docs = client()[DB_NAME][COLLECTION].find({}, {"_id": 0})
    df = pd.DataFrame(list(docs))
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values(["connection", "direction", "date"])

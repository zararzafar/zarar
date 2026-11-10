"""Page 5: about the app and its data sources (the placeholder from part 1, moved from page four)."""
import streamlit as st

st.set_page_config(page_title="IND320 – About", page_icon="ℹ️")
st.title("About")

st.markdown(
    "**Data sources**\n"
    "- Reservoir statistics: [NVE Magasinstatistikk API](https://biapi.nve.no/magasinstatistikk/swagger) "
    "– weekly fill rate and stored energy for Norway, the price areas NO1-NO5 and the water-course areas.\n"
    "- Cross-border flows: [ENTSO-E Transparency Platform](https://transparency.entsoe.eu/) – "
    "prepared in the Jupyter Notebook (Cassandra + Spark) and stored in MongoDB.\n\n"
    "**Code:** [GitHub](https://github.com/zararzafar/zarar)\n\n"
    "Later parts of the project will add more analysis and prediction features."
)

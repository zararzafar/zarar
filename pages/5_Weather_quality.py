"""Page 5: outliers (SPC) in precipitation and anomalies (LOF) in temperature (two tabs).

The weather area follows the global area selector used for the reservoir data, so changing the
area there changes which weather data are downloaded. The year is a local setting for this page.
"""
import pandas as pd
import streamlit as st

from analysis import precipitation_spc, temperature_lof
from nve_api import area_controls, area_names
from weather import download_weather, region_for

st.set_page_config(page_title="IND320 – Weather quality", page_icon="🌦️", layout="wide")
st.title("Weather data quality")

area_type, area_number = area_controls()
region = region_for(area_type, area_number)
name = area_names().get((area_type, area_number), region)

with st.sidebar:
    st.header("Weather")
    this_year = pd.Timestamp.now().year
    year = st.selectbox("Year", options=list(range(this_year - 1, 1999, -1)),
                        index=1 if this_year - 2 >= 2000 else 0)   # default: the year before last

# Download (cached): hourly ERA5 data averaged over random locations in the chosen area
weather = download_weather(region, year)
st.caption(f"Hourly ERA5 reanalysis from open-meteo for **{name}** ({region}) in {year}, "
           f"averaged over 5 random locations inside the area. {len(weather)} hours.")

tab_spc, tab_lof = st.tabs(["Outliers in precipitation (SPC)", "Anomalies in temperature (LOF)"])

with tab_spc:
    c1, c2 = st.columns(2)
    cutoff = c1.slider("DCT cut-off (number of removed low frequencies)", 5, 300, 50, step=5)
    n_std = c2.slider("Number of robust standard deviations", 1.0, 6.0, 3.0, step=0.5)
    fig, summary = precipitation_spc(weather["precipitation"], cutoff=cutoff, n_std=n_std)
    st.pyplot(fig)
    m1, m2, m3 = st.columns(3)
    m1.metric("Outliers", summary["n_outliers"], f"{summary['share_outliers']:.1%} of the hours",
              delta_color="off")
    m2.metric("Above upper limit", summary["n_above"])
    m3.metric("Robust SD of SATV", f"{summary['satv_robust_sd']:.3f} mm")
    with st.expander("Largest outliers"):
        st.dataframe(summary["outliers"].sort_values("precipitation_mm", ascending=False).head(20),
                     use_container_width=True)

with tab_lof:
    c1, c2 = st.columns(2)
    contamination = c1.slider("Proportion of anomalies", 0.001, 0.05, 0.01, step=0.001, format="%.3f")
    n_neighbors = c2.slider("Number of neighbours (hours)", 10, 200, 48, step=2)
    fig, summary = temperature_lof(weather["temperature_2m"], contamination=contamination,
                                   n_neighbors=n_neighbors)
    st.pyplot(fig)
    m1, m2, m3 = st.columns(3)
    m1.metric("Anomalies", summary["n_anomalies"])
    m2.metric("Mean temperature of anomalies", f"{summary['mean_temp_anomalies']:.1f} °C")
    m3.metric("Mean temperature (all hours)", f"{summary['mean_temp_all']:.1f} °C")
    with st.expander("Strongest anomalies"):
        st.dataframe(summary["anomalies"].head(20), use_container_width=True)

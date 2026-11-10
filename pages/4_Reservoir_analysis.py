"""Page 4: STL decomposition and spectrogram of the reservoir fill rate (two tabs)."""
import streamlit as st

from analysis import fill_spectrogram, stl_decomposition
from nve_api import AREA_TYPES, area_controls, area_names, download, month_options

st.set_page_config(page_title="IND320 – Reservoir analysis", page_icon="🌀", layout="wide")
st.title("Reservoir analysis")

# Global area selector (shared with the other pages through session state)
area_type, area_number = area_controls()
name = area_names().get((area_type, area_number), f"{area_type}{area_number}")

# The whole history is used here, because STL and spectrograms need many years of data
months = month_options()
df = download(months[0], months[-1])
series = (df[(df["area_type"] == area_type) & (df["area_number"] == area_number)]
          .set_index("date")["fill_rate"])

if series.empty:
    st.warning("No reservoir data for this area.")
    st.stop()

st.caption(f"Weekly fill rate for **{name}** ({AREA_TYPES[area_type]}), "
           f"{series.index.min():%d.%m.%Y} to {series.index.max():%d.%m.%Y}. Source: NVE Magasinstatistikk API.")

tab_stl, tab_spec = st.tabs(["STL decomposition", "Spectrogram"])

with tab_stl:
    # Local settings for STL (they only apply to this tab)
    c1, c2, c3 = st.columns(3)
    seasonal = c1.select_slider("Seasonal smoother (weeks)", options=list(range(7, 54, 2)), value=13)
    trend = c2.select_slider("Trend smoother (weeks)", options=list(range(53, 262, 4)), value=105)
    robust = c3.checkbox("Robust fitting", value=True)
    st.pyplot(stl_decomposition(series, seasonal=seasonal, trend=trend, robust=robust, title=f"of {name}"))
    st.caption("The trend smoother must be longer than the period (52 weeks); both smoothers use odd lengths.")

with tab_spec:
    c1, c2 = st.columns(2)
    window = c1.slider("Window length (weeks)", min_value=26, max_value=260, value=104, step=2)
    overlap = c2.slider("Window overlap (weeks)", min_value=0, max_value=window - 2,
                        value=min(78, window - 2), step=2)
    st.pyplot(fill_spectrogram(series, window_length=window, overlap=overlap, title=f"of {name}"))
    st.caption("Frequency in cycles per year: the yearly filling and emptying cycle appears at 1.")

"""Analysis functions for IND320 part 3 (shared by the notebook and the Streamlit app)."""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.fft import dct, idct
from scipy.signal import spectrogram
from scipy.stats import median_abs_deviation
from sklearn.neighbors import LocalOutlierFactor


def precipitation_spc(precip: pd.Series, cutoff: int = 50, n_std: float = 3.0):
    """Statistical Process Control (SPC) for precipitation, based on DCT high-pass filtering.

    precip : hourly (average) precipitation with a DatetimeIndex
    cutoff : number of the lowest DCT coefficients that are removed (the high-pass cut-off).
             Index k corresponds to a period of about 2*N/k samples, so for one year of hourly
             data the default 50 removes variations slower than roughly two weeks.
    n_std  : number of robust standard deviations between the centre and the SPC limits

    Returns (fig, summary) where summary is a dict with statistics and a table of the outliers.
    """
    values = precip.to_numpy(dtype=float)

    # DCT of the whole series; setting the lowest coefficients to zero gives a high-pass filter.
    coeffs = dct(values, norm="ortho")
    coeffs[:cutoff] = 0
    satv = idct(coeffs, norm="ortho")          # seasonally adjusted variations (SATV)
    slow = values - satv                       # the slowly varying (seasonal) part

    # Robust statistics of the SATV for the whole period: median and MAD scaled to a standard deviation
    centre = np.median(satv)
    robust_sd = median_abs_deviation(satv, scale="normal")
    upper_satv = centre + n_std * robust_sd
    lower_satv = centre - n_std * robust_sd
    is_outlier = (satv > upper_satv) | (satv < lower_satv)

    # The SPC limits are drawn around the slowly varying part of the original series,
    # so the SATV values themselves are never plotted.
    upper = slow + upper_satv
    lower = slow + lower_satv

    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.plot(precip.index, values, color="tab:blue", linewidth=0.6, label="Precipitation")
    ax.plot(precip.index, upper, color="tab:green", linewidth=1, label=f"SPC limits (±{n_std:g} robust SD)")
    ax.plot(precip.index, lower, color="tab:green", linewidth=1)
    ax.scatter(precip.index[is_outlier], values[is_outlier], color="tab:red", s=12, zorder=3,
               label=f"Outliers ({is_outlier.sum()})")
    ax.set_title(f"Precipitation with SPC limits (DCT cut-off = {cutoff})")
    ax.set_xlabel("Time")
    ax.set_ylabel("Precipitation (mm per hour)")
    ax.grid(alpha=0.3)
    ax.legend(loc="upper left", fontsize=8)
    fig.tight_layout()

    outliers = pd.DataFrame({"precipitation_mm": values[is_outlier],
                             "satv": satv[is_outlier]}, index=precip.index[is_outlier])
    summary = {
        "n_values": len(values),
        "n_outliers": int(is_outlier.sum()),
        "share_outliers": float(is_outlier.mean()),
        "n_above": int((satv > upper_satv).sum()),
        "n_below": int((satv < lower_satv).sum()),
        "satv_median": float(centre),
        "satv_robust_sd": float(robust_sd),
        "cutoff": cutoff,
        "n_std": n_std,
        "outliers": outliers,
    }
    return fig, summary


def temperature_lof(temp: pd.Series, contamination: float = 0.01, n_neighbors: int = 48,
                    time_scale_days: float = 3.0):
    """Anomaly detection for temperature with the Local Outlier Factor (LOF).

    Each observation is described by two standardised features: its time and its temperature.
    Time is scaled so that `time_scale_days` days count as much as one standard deviation of the
    temperature, which makes the method compare each value with its neighbours in time.

    contamination : proportion of points that are classified as anomalies (default 1 %)
    n_neighbors   : number of neighbours used by LOF (48 = two days of hourly values)

    Returns (fig, summary).
    """
    values = temp.to_numpy(dtype=float)
    hours = (temp.index - temp.index[0]) / pd.Timedelta(hours=1)
    X = np.column_stack([
        np.asarray(hours, dtype=float) / (24 * time_scale_days),
        (values - values.mean()) / values.std(),
    ])

    lof = LocalOutlierFactor(n_neighbors=n_neighbors, contamination=contamination)
    labels = lof.fit_predict(X)                 # -1 = anomaly, 1 = normal
    scores = -lof.negative_outlier_factor_      # larger score = more anomalous
    is_anomaly = labels == -1

    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.plot(temp.index, values, color="tab:blue", linewidth=0.6, label="Temperature")
    ax.scatter(temp.index[is_anomaly], values[is_anomaly], color="tab:red", s=12, zorder=3,
               label=f"LOF anomalies ({is_anomaly.sum()})")
    ax.set_title(f"Temperature with Local Outlier Factor anomalies (proportion = {contamination:.1%})")
    ax.set_xlabel("Time")
    ax.set_ylabel("Temperature 2 m (°C)")
    ax.grid(alpha=0.3)
    ax.legend(loc="upper left", fontsize=8)
    fig.tight_layout()

    anomalies = pd.DataFrame({"temperature_C": values[is_anomaly], "lof_score": scores[is_anomaly]},
                             index=temp.index[is_anomaly]).sort_values("lof_score", ascending=False)
    summary = {
        "n_values": len(values),
        "n_anomalies": int(is_anomaly.sum()),
        "share_anomalies": float(is_anomaly.mean()),
        "contamination": contamination,
        "n_neighbors": n_neighbors,
        "mean_temp_anomalies": float(values[is_anomaly].mean()) if is_anomaly.any() else float("nan"),
        "mean_temp_all": float(values.mean()),
        "anomalies": anomalies,
    }
    return fig, summary


def stl_decomposition(series: pd.Series, period: int = 52, seasonal: int = 13,
                      trend: int = 105, robust: bool = True, title: str = ""):
    """Seasonal-Trend decomposition using LOESS (STL) of a weekly series.

    period   : length of one season (52 weeks = one year)
    seasonal : length of the seasonal smoother (odd, >= 7)
    trend    : length of the trend smoother (odd, > period); 105 weeks is about two years
    robust   : use robust weights that reduce the influence of outliers
    """
    from statsmodels.tsa.seasonal import STL   # imported here so the other functions work without it

    result = STL(series, period=period, seasonal=seasonal, trend=trend, robust=robust).fit()
    fig = result.plot()
    fig.set_size_inches(11, 8)
    fig.suptitle(f"STL decomposition {title} (seasonal={seasonal}, trend={trend}, robust={robust})",
                 y=1.01)
    fig.tight_layout()
    return fig


def fill_spectrogram(series: pd.Series, window_length: int = 104, overlap: int = 78,
                     samples_per_year: float = 52.0, title: str = ""):
    """Spectrogram of a weekly series.

    window_length : number of weeks in each window (104 = two years)
    overlap       : number of weeks two neighbouring windows have in common
    The frequency axis is in cycles per year, so the yearly cycle is at 1.
    """
    values = series.to_numpy(dtype=float)
    f, t, Sxx = spectrogram(values - values.mean(), fs=samples_per_year,
                            nperseg=window_length, noverlap=overlap)
    # t is in years from the start of the series: convert to dates for the x-axis
    times = series.index[0] + pd.to_timedelta(t * 365.25, unit="D")

    fig, ax = plt.subplots(figsize=(11, 4.5))
    mesh = ax.pcolormesh(times, f, 10 * np.log10(Sxx + 1e-12), shading="gouraud", cmap="viridis")
    fig.colorbar(mesh, ax=ax, label="Power (dB)")
    ax.set_title(f"Spectrogram {title} (window = {window_length} weeks, overlap = {overlap} weeks)")
    ax.set_xlabel("Time")
    ax.set_ylabel("Frequency (cycles per year)")
    fig.tight_layout()
    return fig

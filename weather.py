"""Weather data for the Streamlit app: NVE area polygons, random locations and open-meteo ERA5.

The same steps as in the part 3 notebook, simplified for the app:
- the area polygons are downloaded from NVE's map services (the layers behind atlas.nve.no)
- random locations are drawn inside the chosen area
- hourly ERA5 data are downloaded from open-meteo for a few of these locations and averaged
Everything is cached, so the downloads only happen once per area and year.
"""
import numpy as np
import pandas as pd
import requests
import streamlit as st
from shapely.geometry import Point, shape
from shapely.ops import unary_union

PRICE_AREA_URL = "https://kart.nve.no/enterprise/rest/services/Nettomraader/MapServer/0"
NVE_REGION_URL = "https://gis3.nve.no/map/rest/services/Mapservices/Administrasjon2/MapServer/0"
ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
HOURLY_VARIABLES = ["temperature_2m", "precipitation", "rain", "snowfall",
                    "wind_speed_10m", "relative_humidity_2m"]

# Precipitation areas from NVE's regions (as in the notebook): East = RS + RØ, West = RV, North = RM + RN
TO_PRECIP_AREA = {"RS": "VASS1", "RØ": "VASS1", "RV": "VASS2", "RM": "VASS3", "RN": "VASS3"}


def region_for(area_type: str, area_number: int) -> str:
    """Map the reservoir area selector to a weather region: ('EL', 3) -> 'NO3', ('VASS', 1) -> 'VASS1'."""
    if area_type == "EL":
        return f"NO{area_number}"
    if area_type == "VASS":
        return f"VASS{area_number}"
    return "NO"                      # the whole country


def _layer(url: str) -> list:
    params = {"where": "1=1", "outFields": "*", "outSR": 4326, "f": "geojson",
              "maxAllowableOffset": 0.002, "geometryPrecision": 4}
    response = requests.get(url + "/query", params=params, timeout=120)
    response.raise_for_status()
    return response.json()["features"]


@st.cache_resource(show_spinner="Downloading area polygons from NVE ...")
def area_polygons() -> dict:
    """Region name -> shapely polygon in longitude/latitude."""
    polygons = {}
    price = {f["properties"]["budomr"].replace(" ", ""): shape(f["geometry"]) for f in _layer(PRICE_AREA_URL)}
    polygons.update(price)
    polygons["NO"] = unary_union(list(price.values()))
    groups = {}
    for f in _layer(NVE_REGION_URL):
        region = TO_PRECIP_AREA.get(f["properties"]["REGION"])
        if region:
            groups.setdefault(region, []).append(shape(f["geometry"]))
    polygons.update({region: unary_union(parts) for region, parts in groups.items()})
    return polygons


@st.cache_data(show_spinner=False)
def sample_locations(region: str, n: int = 1000, seed: int = 320) -> pd.DataFrame:
    """n random locations inside the region (rejection sampling in longitude/latitude)."""
    polygon = area_polygons()[region]
    rng = np.random.default_rng(seed)
    minx, miny, maxx, maxy = polygon.bounds
    points = []
    while len(points) < n:
        for x, y in zip(rng.uniform(minx, maxx, 2 * n), rng.uniform(miny, maxy, 2 * n)):
            if polygon.contains(Point(x, y)):
                points.append((round(x, 4), round(y, 4)))
    return pd.DataFrame(points[:n], columns=["longitude", "latitude"])


@st.cache_data(ttl=7 * 24 * 3600, show_spinner="Downloading ERA5 weather from open-meteo ...")
def download_weather(region: str, year: int, n_locations: int = 5) -> pd.DataFrame:
    """Hourly ERA5 weather for one year, averaged over n random locations in the region."""
    points = sample_locations(region).sample(n_locations, random_state=320)
    params = {
        "latitude": ",".join(points["latitude"].astype(str)),
        "longitude": ",".join(points["longitude"].astype(str)),
        "start_date": f"{year}-01-01",
        "end_date": f"{year}-12-31",
        "hourly": ",".join(HOURLY_VARIABLES),
        "models": "era5",
        "timezone": "UTC",
    }
    response = requests.get(ARCHIVE_URL, params=params, timeout=300)
    response.raise_for_status()
    result = response.json()
    result = [result] if isinstance(result, dict) else result
    frames = [pd.DataFrame(loc["hourly"]) for loc in result]
    data = pd.concat(frames)
    data["time"] = pd.to_datetime(data["time"])
    return data.groupby("time")[HOURLY_VARIABLES].mean()

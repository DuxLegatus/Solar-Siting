import geopandas as gpd
import pandas as pd
from utils import get_grid_points
from shapely.geometry import Point
from config import GRID_ACCESSIBILITY_CSV


grid_points = get_grid_points()
print(grid_points)

grid_points = gpd.GeoDataFrame(
    grid_points,
    geometry=[
        Point(i["lon"], i["lat"])
        for i in grid_points
        ],
    crs="EPSG:4326"
)

power_lines = gpd.read_file("../data/raw/power_lines.geojson")
substations = gpd.read_file("../data/raw/substations.geojson")
power_lines["voltage"] = power_lines["tags"].apply(
    lambda x: x.get("voltage") if isinstance(x, dict) else None
)
power_lines["voltage"] = pd.to_numeric(
    power_lines["voltage"],
    errors="coerce"
)
power_lines["voltage"].value_counts(dropna=False)
high_voltage_lines = power_lines[
    power_lines["voltage"] >= 110000
]
power_lines["operator"] = power_lines["tags"].apply(
    lambda x: x.get("operator") if isinstance(x, dict) else None
)

power_lines["name"] = power_lines["tags"].apply(
    lambda x: x.get("name") if isinstance(x, dict) else None
)

power_lines["cables"] = power_lines["tags"].apply(
    lambda x: x.get("cables") if isinstance(x, dict) else None
)

high_voltage_lines = high_voltage_lines.to_crs("EPSG:32638")
substations = substations.to_crs("EPSG:32638")
grid_points = grid_points.to_crs("EPSG:32638")

grid_points = gpd.sjoin_nearest(
    grid_points,
    high_voltage_lines[["voltage","geometry"]],
    how="left",
    distance_col="distance_to_line"
)
grid_points = grid_points.drop(columns=["index_right"])
grid_points = gpd.sjoin_nearest(
    grid_points,
    substations[["geometry"]],
    how="left",
    distance_col="distance_to_substation"
)

grid_points["line_score"]=(
    1/(1+grid_points["distance_to_line"]/25000)
)
grid_points["substation_score"] = (
    1/(1 + grid_points["distance_to_substation"] / 25000)
)

grid_points["grid_score"] = (
    (grid_points["substation_score"] + grid_points["line_score"])/2
)

grid_points = grid_points.to_crs("EPSG:4326")
grid_points.drop(
    columns="geometry"
).to_csv(
    GRID_ACCESSIBILITY_CSV,
    index=False
)
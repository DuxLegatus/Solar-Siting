import geopandas as gpd
import numpy as np
from shapely.geometry import Point
from config import NATURAL_EARTH_SHP,GRID_POINTS_CSV,GRID_LAT_MAX,GRID_LAT_MIN,GRID_LON_MAX,GRID_LON_MIN,GRID_STEP

world = gpd.read_file(NATURAL_EARTH_SHP)
georgia = world[world["NAME"] == "Georgia"]  

if georgia.empty:
    print("Couldn't find 'Georgia' — check available names:")
    print(world["NAME"].unique())
else:
    georgia_geom = georgia.geometry.iloc[0]

    lat_range = np.arange(GRID_LAT_MIN, GRID_LAT_MAX, GRID_STEP)
    lon_range = np.arange(GRID_LON_MIN, GRID_LON_MAX, GRID_STEP)

    grid_points = []
    for lat in lat_range:
        for lon in lon_range:
            point = Point(lon, lat) 
            if georgia_geom.contains(point):
                grid_points.append({"lat": round(lat, 3), "lon": round(lon, 3)})

    print(f"{len(grid_points)} grid points fall inside Georgia")

    import csv
    with open(GRID_POINTS_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["lat", "lon"])
        writer.writeheader()
        writer.writerows(grid_points)
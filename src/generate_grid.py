import geopandas as gpd
import numpy as np
from shapely.geometry import Point

world = gpd.read_file("data/raw/naturalearth/ne_10m_admin_0_countries.shp")
georgia = world[world["NAME"] == "Georgia"]  

if georgia.empty:
    print("Couldn't find 'Georgia' — check available names:")
    print(world["NAME"].unique())
else:
    georgia_geom = georgia.geometry.iloc[0]

    lat_range = np.arange(41.0, 43.6, 0.25)
    lon_range = np.arange(40.0, 46.6, 0.25)

    grid_points = []
    for lat in lat_range:
        for lon in lon_range:
            point = Point(lon, lat) 
            if georgia_geom.contains(point):
                grid_points.append({"lat": round(lat, 3), "lon": round(lon, 3)})

    print(f"{len(grid_points)} grid points fall inside Georgia")

    import csv
    with open("data/processed/georgia_grid_points.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["lat", "lon"])
        writer.writeheader()
        writer.writerows(grid_points)
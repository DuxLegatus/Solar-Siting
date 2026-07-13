import rasterio
import csv
from config import DEM_TIF,GRID_POINTS_CSV,ELEVATION_CSV

from utils import get_grid_points
results = []
grid_points = get_grid_points()

with rasterio.open(DEM_TIF) as src:
    for (lon, lat), val in zip(grid_points, src.sample(grid_points)):
        results.append({
            "latitude": lat,
            "longitude": lon,
            "elevation": val[0]  
        })


with open(ELEVATION_CSV, "w", newline="") as csvfile:
    fieldnames = ["latitude","longitude","elevation"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)
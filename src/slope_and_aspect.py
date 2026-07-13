import json
import csv
import rasterio
from config import GRID_POINTS_CSV, SLOPE_TIF,SLOPE_ASPECT_CSV,ASPECT_TIF
from utils import get_grid_points
grid_points = get_grid_points()

results = []

with rasterio.open(SLOPE_TIF) as slope_src, \
     rasterio.open(ASPECT_TIF) as aspect_src:
        slope_gen = slope_src.sample(grid_points)
        aspect_gen = aspect_src.sample(grid_points)
        
        for (lon, lat), slope_val, aspect_val in zip(grid_points, slope_gen, aspect_gen):
            results.append({
                "latitude": lat,
                "longitude": lon,
                "slope": slope_val[0],
                "aspect": aspect_val[0]
            })

with open(SLOPE_ASPECT_CSV, "w", newline="") as csvfile:
    fieldnames = ["latitude","longitude","slope","aspect"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)


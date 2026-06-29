import json
import csv
import rasterio
grid_points = []
with open("../data/processed/georgia_grid_points.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        grid_points.append((float(row["lon"]), float(row["lat"])))

results = []

with rasterio.open("../data/raw/dem/slope.tif") as slope_src, \
     rasterio.open("../data/raw/dem/aspect.tif") as aspect_src:
        slope_gen = slope_src.sample(grid_points)
        aspect_gen = aspect_src.sample(grid_points)
        
        for (lon, lat), slope_val, aspect_val in zip(grid_points, slope_gen, aspect_gen):
            results.append({
                "latitude": lat,
                "longitude": lon,
                "slope": slope_val[0],
                "aspect": aspect_val[0]
            })

with open("../data/processed/georgia_slope_aspect.csv", "w", newline="") as csvfile:
    fieldnames = ["latitude","longitude","slope","aspect"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)


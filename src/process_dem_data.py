import rasterio
import csv

grid_points = []
results = []
with open("../data/processed/georgia_grid_points.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        grid_points.append((float(row["lon"]), float(row["lat"])))

with rasterio.open("../data/raw/dem/output_SRTMGL1.tif") as src:
    for (lon, lat), val in zip(grid_points, src.sample(grid_points)):
        results.append({
            "latitude": lat,
            "longitude": lon,
            "elevation": val[0]  
        })


with open("../data/processed/georgia_elevation.csv", "w", newline="") as csvfile:
    fieldnames = ["latitude","longitude","elevation"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)
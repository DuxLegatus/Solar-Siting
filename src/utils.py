import csv
from config import GRID_POINTS_CSV


def get_grid_points():
    grid_points = []
    with open(GRID_POINTS_CSV, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            grid_points.append({"lat": float(row["lat"]), "lon": float(row["lon"])})
    return grid_points
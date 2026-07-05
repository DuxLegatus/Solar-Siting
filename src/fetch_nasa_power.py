import requests
import time
import json
import csv
grid_points = []
with open("../data/processed/georgia_grid_points.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        grid_points.append({"lat": float(row["lat"]), "lon": float(row["lon"])})

print(f"Loaded {len(grid_points)} grid points")
results = []

for point in grid_points:
    url = "https://power.larc.nasa.gov/api/temporal/monthly/point"
    params = {
        "parameters": "ALLSKY_SFC_SW_DWN",
        "community": "RE",
        "longitude": point["lon"],
        "latitude": point["lat"],
        "start": 2015,
        "end": 2025,
        "format": "JSON"
    }

    response = requests.get(url, params=params)
    data = response.json()

    filename = f"../data/raw/nasa_power_{point['lat']}_{point['lon']}.json"
    with open(filename, "w") as f:
        json.dump(data, f)

    results.append({"lat": point["lat"], "lon": point["lon"], "raw_data": data})

    print(f"Fetched {point['lat']}, {point['lon']}")
    time.sleep(0.5)

print(f"Done — fetched {len(results)} points")
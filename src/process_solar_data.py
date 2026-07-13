import os
import json
import csv
from config import NASA_POWER_RAW_CSV
path =  "../data/raw"

contents = os.listdir(path)
results = []
for content in contents:
    full_path = os.path.join(path, content)
    if content == "natural_earth" or os.path.isdir(full_path):
        continue
    with open(f"{path}/{content}","r") as f:
        data = json.load(f)
        latitude = data["geometry"]["coordinates"][1]
        longitude = data["geometry"]["coordinates"][0]
        irradiance = data["properties"]["parameter"]["ALLSKY_SFC_SW_DWN"]
    for i in irradiance:
        data_writing = {
            "latitude": latitude,
            "longitude": longitude,
            "year_month": i, # there is going to be 13 months in total, 13th month is average irradiance through the whole year
            "irradiance": irradiance[i]
        }
        results.append(data_writing)

with open(NASA_POWER_RAW_CSV, 'w', newline='') as csvfile:
    fieldnames = ['latitude', 'longitude', 'year_month', 'irradiance']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)
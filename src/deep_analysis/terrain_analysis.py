import rasterio
import numpy as np
import csv

results = []

for i in range(1,4):
    with rasterio.open(f"../data/raw/deep_analysis/site_{i}_slope.tif") as src:
        data_slope = src.read(1,masked = True)

    with rasterio.open(f"../data/raw/deep_analysis/site_{i}_aspect.tif") as src:
        data_aspect = src.read(1, masked = True)

    south = np.ma.mean((data_aspect >= 157.5) & (data_aspect < 202.5))

    southeast_southwest = np.ma.mean(
        ((data_aspect >= 112.5) & (data_aspect < 157.5)) |
        ((data_aspect >= 202.5) & (data_aspect < 247.5))
    )

    east_west = np.ma.mean(
        ((data_aspect >= 67.5) & (data_aspect < 112.5)) |
        ((data_aspect >= 247.5) & (data_aspect < 292.5))
    )

    northeast_northwest = np.ma.mean(
        ((data_aspect >= 22.5) & (data_aspect < 67.5)) |
        ((data_aspect >= 292.5) & (data_aspect < 337.5))
    )

    north = np.ma.mean(
        (data_aspect >= 337.5) |
        (data_aspect < 22.5)
    )

    aspect_score = (south * 1.0 +southeast_southwest * 0.9 +east_west * 0.6 +northeast_northwest * 0.4 +north * 0.2)
    slope_score = (np.ma.mean(data_slope<5))*1+(np.ma.mean(data_slope<10)-np.ma.mean(data_slope<5))*0.8+(np.ma.mean(data_slope<15)-np.ma.mean(data_slope<10))*0.5+(1-(np.ma.mean(data_slope<15)))*0
    terrain_score = 0.7*(slope_score)+0.3*(aspect_score)
    results.append({
        "site":f"site_{i}",
        "min_slope":data_slope.min(),
        "max_slope":data_slope.max(),
        "mean_slope":data_slope.mean(),
        "median_slope":np.ma.median(data_slope),
        "slope < 5 (%)": np.ma.mean(data_slope<5)*100,
        "slope < 10 (%)": np.ma.mean(data_slope<10)*100,
        "slope < 15 (%)": np.ma.mean(data_slope<15)*100,
        "south oriented aspect (%)": np.ma.mean((data_aspect<=247.5)&(data_aspect>=112.5))*100,
        "slope_score":slope_score,
        "aspect_score":aspect_score,
        "terrain_suitability": terrain_score
    })

with open("../data/processed/deep_analysis/terrain_analysis.csv","w",newline="") as csvfile:
    fieldnames = ["site","min_slope", "max_slope", "mean_slope", "median_slope","slope < 5 (%)","slope < 10 (%)","slope < 15 (%)","south oriented aspect (%)","slope_score","aspect_score","terrain_suitability"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)
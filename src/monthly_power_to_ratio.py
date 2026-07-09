import pandas as pd 
import csv
import rasterio

data = pd.read_csv("../data/processed/solar_irradiance_monthly_avg.csv")
ratios = []

for (lat,lon), group in data.groupby(["latitude","longitude"]):
    annual_value = group.loc[group["month"] == 13, "irradiance"].values[0]
    for _, row in group[group["month"] != 13].iterrows():
        ratios.append({
            "latitude": lat,
            "longitude": lon,
            "month": row["month"],
            "monthly_ratio": row["irradiance"] / annual_value
        })
ratios_df = pd.DataFrame(ratios)
grid_points = []

with open("../data/processed/georgia_grid_points.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        grid_points.append((float(row["lon"]), float(row["lat"])))

def sample_annual_raster(path, colname):
    results = []
    with rasterio.open(path) as src:
        for (lon, lat), val in zip(grid_points, src.sample(grid_points)):
            results.append({"latitude": lat, "longitude": lon, colname: val[0]})
    return pd.DataFrame(results)


ghi_df = sample_annual_raster("../data/raw/validation/GHI.tif", "ghi_annual")
dni_df = sample_annual_raster("../data/raw/validation/DNI.tif", "dni_annual")
dif_df = sample_annual_raster("../data/raw/validation/DIF.tif", "dif_annual")

final_df = (
    ratios_df
    .merge(ghi_df, on=["latitude", "longitude"], how="left")
    .merge(dni_df, on=["latitude", "longitude"], how="left")
    .merge(dif_df, on=["latitude", "longitude"], how="left")
)

final_df["ghi_monthly"] = final_df["ghi_annual"] * final_df["monthly_ratio"]
final_df["dni_monthly"] = final_df["dni_annual"] * final_df["monthly_ratio"]
final_df["dif_monthly"] = final_df["dif_annual"] * final_df["monthly_ratio"]

final_df = final_df.drop(columns=["ghi_annual", "dni_annual", "dif_annual","monthly_ratio"])
final_df.to_csv("../data/processed/georgia_irradiance_downscaled.csv", index=False)
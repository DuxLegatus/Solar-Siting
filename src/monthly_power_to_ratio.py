import pandas as pd 
import csv
import rasterio
from config import NASA_POWER_MONTHLY_AVG_CSV,GRID_POINTS_CSV,GSA_DIF_TIF,GSA_DNI_TIF,GSA_GHI_TIF,IRRADIANCE_DOWNSCALED_CSV
from utils import get_grid_points
data = pd.read_csv(NASA_POWER_MONTHLY_AVG_CSV)
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

grid_points = get_grid_points()

def sample_annual_raster(path, colname):
    results = []
    with rasterio.open(path) as src:
        for (lon, lat), val in zip(grid_points, src.sample(grid_points)):
            results.append({"latitude": lat, "longitude": lon, colname: val[0]})
    return pd.DataFrame(results)


ghi_df = sample_annual_raster(GSA_GHI_TIF, "ghi_annual")
dni_df = sample_annual_raster(GSA_DNI_TIF, "dni_annual")
dif_df = sample_annual_raster(GSA_DIF_TIF, "dif_annual")

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
final_df.to_csv(IRRADIANCE_DOWNSCALED_CSV, index=False)
import time
import numpy as np
import pandas as pd
import requests
import matplotlib.pyplot as plt
from config import SOLAR_DATA_FINAL_CSV,PVGIS_ERROR_BY_MONTH_PNG,PVGIS_ERROR_VS_SLOPE_PNG,PVGIS_POA_CSV,PVGIS_ERROR_HISTOGRAM_PNG,PVGIS_SCATTER_PNG,PVGIS_VALIDATION_CSV

final_data = pd.read_csv(SOLAR_DATA_FINAL_CSV)
points = final_data[["latitude","longitude","slope","aspect"]].drop_duplicates(subset =["latitude","longitude"]).dropna(subset=["slope","aspect"])

DAYS_IN_MONTH = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30,
                  7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}

results = []

for i,row in points.iterrows():
    lat = row["latitude"]
    lon = row["longitude"]
    slope = row["slope"]
    aspect = row["aspect"]
    pvgis_aspect =  aspect -180

    url = "https://re.jrc.ec.europa.eu/api/v5_3/MRcalc"
    params = {
        "lat" : lat,
        "lon": lon,
        "angle": slope,
        "aspect": pvgis_aspect,
        "selectrad": 1,
        "outputformat": "json"
    }

    try:
        response = requests.get(url=url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        monthly = data["outputs"]["monthly"]
        monthly_df = pd.DataFrame(monthly)
        monthly_avg = monthly_df.groupby("month")["H(i)_m"].mean()
        for month in range(1,13):
            h_i_m = monthly_avg.get(month)
            if h_i_m is not None:
                h_i_d = h_i_m/ DAYS_IN_MONTH[month]
                results.append({
                    "latitude":lat, "longitude":lon, "month":month, "pvgis_poa": h_i_d
                })
    except Exception as e:
        print(f"Failed at ({lat}, {lon}): {e}")

    time.sleep(0.1)

pvgis_df = pd.DataFrame(results)
pvgis_df.to_csv(PVGIS_POA_CSV,index=False)

merged_df = pd.merge(
    final_data[["latitude","longitude","month","adjusted_irradiance","slope"]],
    pvgis_df,
    on=["latitude","longitude","month"],
    how="inner"
).dropna(subset=["adjusted_irradiance", "pvgis_poa"])

errors = merged_df["adjusted_irradiance"] - merged_df["pvgis_poa"]
abs_error = abs(errors)
percentage_errors = abs_error / merged_df["pvgis_poa"] * 100

MAE = abs_error.mean()
MBE = errors.mean()
RMSE = np.sqrt((errors**2).mean())
MAPE = percentage_errors.mean()
R = merged_df["adjusted_irradiance"].corr(merged_df["pvgis_poa"])
R2 = R**2

print(f"\nPoints compared: {len(merged_df)}")
print(f"MAE:  {MAE:.4f} kWh/m²/day")
print(f"RMSE: {RMSE:.4f} kWh/m²/day")
print(f"MBE:  {MBE:.4f} kWh/m²/day")
print(f"MAPE: {MAPE:.2f}%   Accuracy: {100 - MAPE:.2f}%")
print(f"R:    {R:.4f}   R²: {R2:.4f}")

plt.figure(figsize=(6, 6))
plt.scatter(merged_df["pvgis_poa"], merged_df["adjusted_irradiance"], alpha=0.5)
lims = [min(merged_df["pvgis_poa"].min(), merged_df["adjusted_irradiance"].min()),
        max(merged_df["pvgis_poa"].max(), merged_df["adjusted_irradiance"].max())]
plt.plot(lims, lims, "r--", label="1:1 line")
plt.xlabel("PVGIS POA irradiance (JRC, independent reference)")
plt.ylabel("adjusted_irradiance (pipeline)")
plt.title(f"Independent Validation: adjusted_irradiance vs PVGIS\nR²={R2:.3f}, Accuracy={100 - MAPE:.1f}% (n={len(merged_df)})")
plt.legend()
plt.grid(True)
plt.savefig(PVGIS_SCATTER_PNG, dpi=300, bbox_inches="tight")
plt.close()

plt.figure(figsize=(6, 5))
plt.hist(errors,color="skyblue",bins=30,alpha=0.7)
plt.axvline(0, color="red", linestyle="--", label="zero error")
plt.axvline(errors.mean(), color="green", linestyle="--", label=f"mean = {errors.mean():.3f}")
plt.xlabel("Error (adjusted_irradiance - pvgis_poa)")
plt.ylabel("Count")
plt.title("Distribution of Validation Errors")
plt.legend()
plt.savefig(PVGIS_ERROR_HISTOGRAM_PNG, dpi=300, bbox_inches="tight")
plt.close()


plt.figure(figsize=(7,5))
plt.scatter(merged_df["slope"],errors, alpha=0.5)
plt.axhline(0, color="red", linestyle="--")
plt.xlabel("Slope (degrees)")
plt.ylabel("Error (adjusted_irradiance - pvgis_poa)")
plt.title("Validation Error vs. Terrain Slope")
plt.savefig(PVGIS_ERROR_VS_SLOPE_PNG, dpi=300, bbox_inches="tight")
plt.close()

monthly_error = merged_df.groupby("month").apply(
    lambda g: g["adjusted_irradiance"] - g["pvgis_poa"]
).groupby("month").agg(["mean", "std"])

plt.figure(figsize=(8, 5))
plt.errorbar(monthly_error.index, monthly_error[("adjusted_irradiance","mean")] if isinstance(monthly_error.columns, pd.MultiIndex) else monthly_error["mean"],
             yerr=monthly_error["std"] if "std" in monthly_error else None, fmt="o-", capsize=4)
plt.axhline(0, color="red", linestyle="--")
plt.xlabel("Month")
plt.ylabel("Mean error ± std")
plt.title("Validation Error by Month")
plt.savefig(PVGIS_ERROR_BY_MONTH_PNG, dpi=300, bbox_inches="tight")
plt.close()
 
merged_df["error"] = errors
merged_df.to_csv(PVGIS_VALIDATION_CSV, index=False)

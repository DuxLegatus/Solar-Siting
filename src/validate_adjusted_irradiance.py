import time
import numpy as np
import pandas as pd
import requests
import matplotlib.pyplot as plt


final_data = pd.read_csv("../data/processed/georgia_solar_data_final.csv")
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
pvgis_df.to_csv("../data/processed/georgia_pvgis_poa.csv",index=False)

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
plt.savefig("../docs/adjusted_irradiance_vs_pvgis.png", dpi=300, bbox_inches="tight")
plt.close()
 
merged_df["error"] = errors
merged_df.to_csv("../data/processed/adjusted_irradiance_pvgis_validation.csv", index=False)

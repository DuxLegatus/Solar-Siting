import rasterio
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


data = pd.read_csv("../data/processed/solar_irradiance_monthly_avg.csv")
grid_points = []
results = []
raw_irradiance = data.loc[data["month"] == 13, "irradiance"].reset_index(drop=True)
percentage_errors = []
errors = []
absolute_errors = []
with open("../data/processed/georgia_grid_points.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        grid_points.append((float(row["lon"]), float(row["lat"])))

with rasterio.open("../data/raw/validation/GHI.tif") as src:
    for (lon, lat), val in zip(grid_points, src.sample(grid_points)):
        results.append({
            "latitude": lat,
            "longitude": lon,
            "Raw_irradiance": val[0]  
        })

for i in range(len(results)):
    error = raw_irradiance[i] - results[i]["Raw_irradiance"]
    absolute_error = abs(error)
    error_percentage = absolute_error/results[i]["Raw_irradiance"] * 100

    errors.append(error)
    percentage_errors.append(error_percentage)
    absolute_errors.append(absolute_error)

MAE = np.mean(absolute_errors)
MBE = np.mean(errors)
RMSE = np.sqrt(np.mean(np.array(errors) ** 2))
model = np.array(raw_irradiance)
reference = np.array([r["Raw_irradiance"] for r in results])
R = np.corrcoef(model, reference)[0, 1]
R2 = R ** 2


plt.figure(figsize=(6,6))
plt.scatter(reference, model, alpha=0.5)

min_val = min(reference.min(), model.min())
max_val = max(reference.max(), model.max())
plt.plot([min_val, max_val], [min_val, max_val], 'r--')

plt.xlabel("Solar Atlas (Reference)")
plt.ylabel("Model Irradiance")
plt.title("Validation: Model vs Solar Atlas")
plt.grid(True)

plt.savefig("../docs/model_vs_solar_atlas.png", dpi=300, bbox_inches="tight")
plt.close()

output = pd.DataFrame({
    "reference": reference,
    "model": model,
    "error": errors,
    "absolute_error": absolute_errors,
    "percentage_error": percentage_errors
})

output.to_csv("../data/processed/raw_irradiance_validation_results.csv", index=False)
grouped = output.groupby("model", as_index=False).agg(
    gsa_mean=("reference", "mean"),
    n_points=("reference", "count")
)

r_grouped = grouped["model"].corr(grouped["gsa_mean"])
r2_grouped = r_grouped ** 2

plt.figure(figsize=(6, 6))
plt.scatter(grouped["gsa_mean"], grouped["model"], s=grouped["n_points"] * 30, alpha=0.6)

lims2 = [min(grouped["gsa_mean"].min(), grouped["model"].min()),
         max(grouped["gsa_mean"].max(), grouped["model"].max())]
plt.plot(lims2, lims2, "r--")

plt.xlabel("GSA GHI, averaged per NASA POWER cell")
plt.ylabel("NASA POWER raw_irradiance")
plt.title(f"Resolution-Matched Validation (n={len(grouped)} cells)\nR²={r2_grouped:.3f}")
plt.grid(True)
plt.savefig("../docs/model_vs_solar_atlas_resolution_matched.png", dpi=300, bbox_inches="tight")
plt.close()

grouped.to_csv("../data/processed/raw_irradiance_validation_resolution_matched.csv", index=False)
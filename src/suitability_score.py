import pandas as pd
from config import LANDCOVER_CSV,PROTECTED_AREA_CSV,SOLAR_DATA_FINAL_CSV,SUITABILITY_CSV,IMPORT_SHARE_BY_MONTH,SYSTEM_LOSS_FACTOR, GRID_ACCESSIBILITY_CSV
from utils import (compute_suitability)
landtype = pd.read_csv(LANDCOVER_CSV)
protected_area = pd.read_csv(PROTECTED_AREA_CSV)
landtype = landtype.rename(columns={
    "lat": "latitude",
    "lon": "longitude"
})
grid_accessibility = pd.read_csv(GRID_ACCESSIBILITY_CSV)
grid_accessibility = grid_accessibility.rename(columns={
    "lat": "latitude",
    "lon": "longitude"
})
protected_area = protected_area.rename(columns={
    "lat": "latitude",
    "lon": "longitude"
})
df = pd.read_csv(SOLAR_DATA_FINAL_CSV)
df = df.merge(
    landtype[["latitude", "longitude", "solar_multiplier"]],
    on=["latitude", "longitude"],
    how="left"
)
df = df.merge(
    protected_area[["latitude", "longitude", "protected_multiplier"]],
    on=["latitude", "longitude"],
    how="left"
)
df = df.merge(
    grid_accessibility[["latitude", "longitude", "grid_score"]],
    on=["latitude", "longitude"],
    how="left"
)

duplicates = df.groupby(["latitude", "longitude"]).size()
print(duplicates.max())
df["import_percentage"] = (df["month"].map(IMPORT_SHARE_BY_MONTH)).fillna(0)

baseline = compute_suitability(df)
baseline.to_csv(SUITABILITY_CSV, index=False)

while True:
    solar = input("Enter: Solar Multiplier (if you do not choose it will automatically be 1, please choose value between 0.8 and 1.2): ").strip()
    loss = input("Enter Loss_multiplier: ")
    solar_scale = float(solar)if solar else 1.0
    loss_scale = float(loss)if loss else SYSTEM_LOSS_FACTOR
    result = compute_suitability(df, solar_scale, loss_scale)
    top10 = result.nlargest(10, "suitability_score")
    top10_set = set(top10.apply(lambda r: (r["latitude"], r["longitude"]), axis=1))
    baseline_top10_set = set(baseline.nlargest(10, "suitability_score").apply(lambda r: (r["latitude"], r["longitude"]), axis=1))
    print(f"\nTop 10 under these assumptions:\n{top10[['latitude','longitude','suitability_score']]}")

    save = input("\nSave this scenario? (y/n): ").strip().lower()
    if save == "y":
        name = input("Filename (without .csv): ").strip()
        result.to_csv(f"../data/processed/{name}.csv", index=False)
        print(f"Saved -> ../data/processed/{name}.csv")

    again = input("\nTry another scenario? (y/n): ").strip().lower()
    if again != "y":
        break
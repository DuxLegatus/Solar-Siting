import pandas as pd
from config import LANDCOVER_CSV,PROTECTED_AREA_CSV,SOLAR_DATA_FINAL_CSV,SUITABILITY_CSV,TOTAL_ANNUAL_IMPORTS_GWH,MONTHLY_IMPORTS_GWH,SYSTEM_LOSS_FACTOR

landtype = pd.read_csv(LANDCOVER_CSV)
protected_area = pd.read_csv(PROTECTED_AREA_CSV)
landtype = landtype.rename(columns={
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


df["import_percentage"] = (df["month"].map(MONTHLY_IMPORTS_GWH)).fillna(0)

df["import_weighted_contribution"] = (
    df["adjusted_irradiance"]
    * df["import_percentage"]
    * df["solar_multiplier"]
    * df["protected_multiplier"]
    * SYSTEM_LOSS_FACTOR
).round(2)

result = (
    df.groupby(["latitude", "longitude"], as_index=False)["import_weighted_contribution"]
    .sum()
)

result.rename(columns={"import_weighted_contribution": "suitability_score"}, inplace=True)
result.to_csv(SUITABILITY_CSV, index=False)

least = result.nsmallest(1, "suitability_score")
most = result.nlargest(1, "suitability_score")
print(least,most)
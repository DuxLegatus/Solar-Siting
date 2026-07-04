import pandas as pd


landtype = pd.read_csv("../data/processed/georgia_grid_with_landtype.csv")
protected_area = pd.read_csv("../data/processed/georgia_protected_area.csv")
landtype = landtype.rename(columns={
    "lat": "latitude",
    "lon": "longitude"
})
protected_area = protected_area.rename(columns={
    "lat": "latitude",
    "lon": "longitude"
})
df = pd.read_csv("../data/processed/georgia_solar_data_final.csv")
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
total_energy_import = 790
energy_import = {
    1: round(247/790,2),
    2: round(207/790,2),
    3: round(147/790,2),
    11: round(81/790,2),
    12: round(108/790,2),
}

df["import_percentage"] = (df["month"].map(energy_import)).fillna(0)

df["import_weighted_contribution"] = (
    df["adjusted_irradiance"]
    * df["import_percentage"]
    * df["solar_multiplier"]
    * df["protected_multiplier"]
    * 0.85
).round(2)

result = (
    df.groupby(["latitude", "longitude"], as_index=False)["import_weighted_contribution"]
    .sum()
)

result.rename(columns={"import_weighted_contribution": "suitability_score"}, inplace=True)
result.to_csv("../data/processed/georgia_solar_suitability.csv", index=False)

least = result.nsmallest(1, "suitability_score")
most = result.nlargest(1, "suitability_score")
print(least,most)
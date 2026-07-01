import pandas as pd

df = pd.read_csv("../data/processed/georgia_solar_data_final.csv")
total_energy_import = 790
energy_import = {
    1: round(247/790,2),
    2: round(207/790,2),
    3: round(147/790,2),
    11: round(81/790,2),
    12: round(108/790,2),
}


df["import_percentage"] = (df["month"].map(energy_import)).fillna(0)
df["import_weighted_contribution"] = round(df["adjusted_irradiance"]*df["import_percentage"],2)

result = (
    df.groupby(["latitude", "longitude"], as_index=False)["import_weighted_contribution"]
      .sum()
)
result.rename(columns={"import_weighted_contribution": "suitability_score"}, inplace=True)
# result.to_csv("../data/processed/georgia_solar_suitability.csv", index=False)

least = result.nsmallest(1, "suitability_score")
most = result.nlargest(1, "suitability_score")
print(least,most)
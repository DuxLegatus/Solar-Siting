import pandas as pd
import numpy as np

df_irradiance = pd.read_csv("../data/processed/solar_irradiance_monthly_avg.csv")
df_elevation = pd.read_csv("../data/processed/georgia_elevation.csv")
df_slope_aspect = pd.read_csv("../data/processed/georgia_slope_aspect.csv")
df_irradiance = df_irradiance[df_irradiance["month"]!=13]
df1 = df_elevation.merge(df_slope_aspect)
azimuth_rad = np.radians(180)

merged_df = pd.merge(df1,df_irradiance, on=['latitude', 'longitude'], how="inner")

declination = {
    1: -20.9,
    2: -13.0,
    3: -2.4,
    4: 9.4,
    5: 18.8,
    6: 23.1,
    7: 21.2,
    8: 13.5,
    9: 2.2,
    10: -9.6,
    11: -18.9,
    12: -23.0 
}

merged_df["declination"] = merged_df["month"].map(declination)
merged_df["latitude_rad"] = np.radians(merged_df["latitude"])
merged_df["declination_rad"] = np.radians(merged_df["declination"])
merged_df["slope_rad"] = np.radians(merged_df["slope"])
merged_df["aspect_rad"] = np.radians(merged_df["aspect"])
merged_df["cos_zenith"] = np.sin(merged_df["latitude_rad"]) * np.sin(merged_df["declination_rad"]) + np.cos(merged_df["latitude_rad"]) * np.cos(merged_df["declination_rad"])
merged_df["sin_zenith"] = np.sqrt(1-(merged_df["cos_zenith"]**2))
merged_df["cos_aoi"] = merged_df["cos_zenith"] * np.cos(merged_df["slope_rad"]) + merged_df["sin_zenith"] * np.sin(merged_df["slope_rad"]) * np.cos(azimuth_rad - merged_df["aspect_rad"])
merged_df["cos_aoi"] = np.clip(merged_df["cos_aoi"],0,None)
merged_df["adjusted_irradiance"] = merged_df["irradiance"] * (merged_df["cos_aoi"] / merged_df["cos_zenith"])
filtered_df = merged_df[merged_df['adjusted_irradiance'] < 0]
print(filtered_df, filtered_df["irradiance"])
merged_df.rename(columns={"irradiance":"raw_irradiance"},inplace=True)
merged_df.loc[merged_df["aspect"] == -9999, "aspect"] = np.nan
merged_df.to_csv("../data/processed/georgia_solar_data_full_debug.csv",index=False)

merged_df[["latitude","raw_irradiance","longitude","month","aspect","slope","declination","adjusted_irradiance"]].to_csv("../data/processed/georgia_solar_data_final.csv",index=False)
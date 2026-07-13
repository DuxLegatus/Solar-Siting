import pandas as pd
import numpy as np
from config import IRRADIANCE_DOWNSCALED_CSV,ELEVATION_CSV,SLOPE_ASPECT_CSV,SOLAR_DATA_FINAL_CSV,SOLAR_DATA_DEBUG_CSV,DECLINATION_BY_MONTH

df_irradiance = pd.read_csv(IRRADIANCE_DOWNSCALED_CSV)
df_elevation = pd.read_csv(ELEVATION_CSV)
df_slope_aspect = pd.read_csv(SLOPE_ASPECT_CSV)
df1 = df_elevation.merge(df_slope_aspect)
azimuth_rad = np.radians(180)

merged_df = pd.merge(df1,df_irradiance, on=['latitude', 'longitude'], how="inner")


merged_df.loc[merged_df["aspect"] == -9999, "aspect"] = np.nan
merged_df["declination"] = merged_df["month"].map(DECLINATION_BY_MONTH)
merged_df["latitude_rad"] = np.radians(merged_df["latitude"])
merged_df["declination_rad"] = np.radians(merged_df["declination"])
merged_df["slope_rad"] = np.radians(merged_df["slope"])
merged_df["aspect_rad"] = np.radians(merged_df["aspect"])
merged_df["cos_zenith"] = np.sin(merged_df["latitude_rad"]) * np.sin(merged_df["declination_rad"]) + np.cos(merged_df["latitude_rad"]) * np.cos(merged_df["declination_rad"])
merged_df["sin_zenith"] = np.sqrt(1-(merged_df["cos_zenith"]**2))
merged_df["cos_aoi"] = merged_df["cos_zenith"] * np.cos(merged_df["slope_rad"]) + merged_df["sin_zenith"] * np.sin(merged_df["slope_rad"]) * np.cos(azimuth_rad - merged_df["aspect_rad"])
merged_df["cos_aoi"] = np.clip(merged_df["cos_aoi"],0,None)
merged_df["adjusted_irradiance"] = (
    merged_df["dni_monthly"] * merged_df["cos_aoi"]
    + merged_df["dif_monthly"] * (1 + np.cos(merged_df["slope_rad"])) / 2
)
merged_df.rename(columns={"ghi_monthly": "raw_irradiance"}, inplace=True)
merged_df.to_csv(SOLAR_DATA_DEBUG_CSV,index=False)

merged_df[["latitude","raw_irradiance","longitude","month","aspect","slope","declination","adjusted_irradiance"]].to_csv(SOLAR_DATA_FINAL_CSV,index=False)
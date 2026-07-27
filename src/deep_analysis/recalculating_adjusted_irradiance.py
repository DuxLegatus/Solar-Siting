import rasterio
import numpy as np
from pathlib import Path
import sys
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import DECLINATION_BY_MONTH, IRRADIANCE_DOWNSCALED_CSV

df = pd.read_csv(IRRADIANCE_DOWNSCALED_CSV)
latitudes = [42.0,41.5,41.5]
sites = [
    (42.0, 45.5),
    (41.5, 44.75),
    (41.5, 44.5)
]
azimuth_rad = np.radians(180)
for i, (latitude, longitude) in enumerate(sites, start=1):
    site_irradiance = df[
        (df["latitude"] == latitude) &
        (df["longitude"] == longitude)
    ]
    with rasterio.open(f"../data/raw/deep_analysis/site_{i}_slope.tif") as src:
        data_slope = src.read(1,masked = True)
        profile = src.profile

    with rasterio.open(f"../data/raw/deep_analysis/site_{i}_aspect.tif") as src:
        data_aspect = src.read(1, masked = True)
    
    latitude_rad = np.radians(latitudes[i-1])
    slope_rad = np.radians(data_slope)
    aspect_rad = np.radians(data_aspect)


    for j in range(1,13):
        cos_zenith = (
            np.sin(latitude_rad) * np.sin(np.radians(DECLINATION_BY_MONTH[j]))
            +
            np.cos(latitude_rad) * np.cos(np.radians(DECLINATION_BY_MONTH[j]))
        )
        cos_zenith = np.clip(cos_zenith, -1, 1)
        zenith_rad = np.arccos(cos_zenith)
        cos_aoi = (
            np.cos(zenith_rad)*np.cos(slope_rad)+np.sin(zenith_rad)*np.sin(slope_rad)*np.cos(azimuth_rad-aspect_rad)  
        )
        cos_aoi = np.clip(cos_aoi,0,None)
        monthly_data = site_irradiance[site_irradiance["month"] == j]

        dni = monthly_data["dni_monthly"].iloc[0]
        dif = monthly_data["dif_monthly"].iloc[0]
        adjusted_irradiance = dni*cos_aoi+dif*(1 + np.cos(slope_rad)) / 2
        print(dni, dif)

        output = f"../data/raw/deep_analysis/site_{i}_adjusted_irradiance_{j}.tif"
        output_profile = profile.copy()
        output_profile.update(
            dtype=adjusted_irradiance.dtype,
            nodata=-9999,
            count=1
        )
        with rasterio.open(output, "w", **output_profile) as dst:
            dst.write(adjusted_irradiance.filled(-9999).astype("float32"), 1)
        
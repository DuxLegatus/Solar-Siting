import pandas as pd

deep = pd.read_csv("../data/processed/deep_analysis/terrain_analysis.csv")
national = pd.read_csv("../data/processed/georgia_solar_data_final.csv")

# match each site to its coarse grid point (you'll need each site's lat/lon)
site_coords = {"site_1": (42.0, 45.5), "site_2": (41.5, 44.75), "site_3": (41.5, 44.5)}

for site, (lat, lon) in site_coords.items():
    coarse_slope = national[(national.latitude == lat) & (national.longitude == lon)]["slope"].iloc[0]
    fine_mean = deep[deep.site == site]["mean_slope"].iloc[0]
    fine_range = deep[deep.site == site]["max_slope"].iloc[0] - deep[deep.site == site]["min_slope"].iloc[0]
    print(f"{site}: coarse point = {coarse_slope:.1f}°, fine mean = {fine_mean:.1f}°, fine range = {fine_range:.1f}°")
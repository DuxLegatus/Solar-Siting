import pandas as pd
import matplotlib
import geopandas
import matplotlib.pyplot as plt


data = pd.read_csv("../data/processed/georgia_solar_suitability.csv")

world = geopandas.read_file("../data/raw/naturalearth/ne_10m_admin_0_countries.shp")
georgia = world[world["NAME"] == "Georgia"] 
fig, ax = plt.subplots()

georgia.boundary.plot(ax=ax)
plt.title("Solar Suitability of Georgia") 
plt.xlabel("Longitude")
plt.ylabel("Latitude")
cmap = matplotlib.colors.LinearSegmentedColormap.from_list("my_gradient",["red","yellow","green"])
sc = ax.scatter(data["longitude"], data["latitude"], c=data["suitability_score"], cmap=cmap)
plt.colorbar(sc, ax=ax, label="Solar Suitability Index")

plt.savefig('../docs/solar_suitability.png')
plt.close()
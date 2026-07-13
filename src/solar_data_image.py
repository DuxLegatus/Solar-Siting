import pandas as pd
import matplotlib
import geopandas
import matplotlib.pyplot as plt
from config import SUITABILITY_CSV,NATURAL_EARTH_SHP,SUITABILITY_MAP_PNG


data = pd.read_csv(SUITABILITY_CSV)

world = geopandas.read_file(NATURAL_EARTH_SHP)
georgia = world[world["NAME"] == "Georgia"] 
fig, ax = plt.subplots()

georgia.boundary.plot(ax=ax)
plt.title("Solar Suitability of Georgia") 
plt.xlabel("Longitude")
plt.ylabel("Latitude")
cmap = matplotlib.colors.LinearSegmentedColormap.from_list("my_gradient",["red","yellow","green"])
sc = ax.scatter(data["longitude"], data["latitude"], c=data["suitability_score"], cmap=cmap)
plt.colorbar(sc, ax=ax, label="Solar Suitability Index")

plt.savefig(SUITABILITY_MAP_PNG)
plt.close()
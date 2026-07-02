import pandas as pd
import matplotlib
import geopandas
import matplotlib.pyplot as plt

data = pd.read_csv("../data/processed/georgia_solar_suitability.csv")

world = geopandas.read_file("../data/raw/naturalearth/ne_10m_admin_0_countries.shp")
georgia = world[world["NAME"] == "Georgia"] 
fig, ax = plt.subplots()
georgia.boundary.plot(ax=ax)
plt.show()
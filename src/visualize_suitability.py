import folium
import pandas as pd
import branca.colormap as cm
from config import SUITABILITY_CSV,SUITABILITY_MAP_HTML

data = pd.read_csv(SUITABILITY_CSV)
data["suitability_index"] = round((data["suitability_score"]-data["suitability_score"].min())/(data["suitability_score"].max()-data["suitability_score"].min()),3)
map1 = folium.Map(location=(42,43.5),zoom_control=True,min_zoom=7,max_zoom=10,tiles="CartoDB positron")
linear = cm.LinearColormap(["red", "yellow", "green"], vmin=0, vmax=data["suitability_index"].max(), caption="Winter Solar Suitability Score (kWh/m²/day)")
lat = data["latitude"]
lon = data["longitude"]
score = data["suitability_index"]
for i in range(len(lat)):

    folium.CircleMarker(
        location=[lat[i],lon[i]],
        radius=8,
        popup=folium.Popup(f"lat:{lat[i]}, lon: {lon[i]}, suitability:{score[i]}"),
        fill_color=linear(score[i]),
        fill_opacity =0.9,
        color = linear(score[i])
    ).add_to(map1)
linear.add_to(map1)
title_html = '''
             <h3 align="center" style="font-size:20px"><b>Optimal Solar Deployment Regions in Georgia: Winter-Weighted Suitability Analysis</b></h3>
             '''
map1.get_root().html.add_child(folium.Element(title_html))

map1.save(SUITABILITY_MAP_HTML)
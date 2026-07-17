import pandas as pd
import geopandas as gpd
from config import WDPA_SHAPEFILES,GRID_POINTS_CSV,PROTECTED_AREA_CSV

file1 = gpd.read_file(WDPA_SHAPEFILES[0])
file2 = gpd.read_file(WDPA_SHAPEFILES[1])
file3 = gpd.read_file(WDPA_SHAPEFILES[2])

main = gpd.GeoDataFrame(
    pd.concat([file1, file2, file3], ignore_index=True),
    crs=file1.crs
)

MIN_PROTECTED_AREA_KM2 = 2.0
main = main[main["GIS_AREA"] >= MIN_PROTECTED_AREA_KM2]

grid = pd.read_csv(GRID_POINTS_CSV)
grid_gdf = gpd.GeoDataFrame(
    grid,
    geometry=gpd.points_from_xy(grid["lon"], grid["lat"]),
    crs="EPSG:4326"
)

main = main.to_crs(grid_gdf.crs)

joined = gpd.sjoin(grid_gdf, main, how="left", predicate="within")
joined["protected_multiplier"] = joined["index_right"].isna().astype(int)
joined = joined.groupby(["lat", "lon"], as_index=False)["protected_multiplier"].min()

joined.to_csv(PROTECTED_AREA_CSV, index=False)
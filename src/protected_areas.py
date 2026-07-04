import pandas as pd
import geopandas as gpd

file1 = gpd.read_file("../data/raw/WDPA_WDOECM_Jul2026_Public_GEO_shp_0/WDPA_WDOECM_Jul2026_Public_GEO_shp-polygons.shp")
file2 = gpd.read_file("../data/raw/WDPA_WDOECM_Jul2026_Public_GEO_shp_1/WDPA_WDOECM_Jul2026_Public_GEO_shp-polygons.shp")
file3 = gpd.read_file("../data/raw/WDPA_WDOECM_Jul2026_Public_GEO_shp_2/WDPA_WDOECM_Jul2026_Public_GEO_shp-polygons.shp")

main = gpd.GeoDataFrame(
    pd.concat([file1, file2, file3], ignore_index=True),
    crs=file1.crs
)

grid = pd.read_csv("../data/processed/georgia_grid_points.csv")

grid_gdf = gpd.GeoDataFrame(
    grid,
    geometry=gpd.points_from_xy(grid["lon"], grid["lat"]),
    crs="EPSG:4326"
)

main = main.to_crs(grid_gdf.crs)

joined = gpd.sjoin(
    grid_gdf,
    main,
    how="left",
    predicate="within"
)

# 1 = not protected, 0 = protected
joined["protected_multiplier"] = joined["index_right"].isna().astype(int)

# collapse duplicates safely
joined = (
    joined.groupby(["lat", "lon"], as_index=False)["protected_multiplier"]
    .min()
)

joined.to_csv(
    "../data/processed/georgia_protected_area.csv",
    index=False
)


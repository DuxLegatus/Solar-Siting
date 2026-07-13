import rasterio
import pandas as pd
import numpy as np
from pathlib import Path
from config import WORLDCOVER_TILES_DIR,GRID_POINTS_CSV,LANDCOVER_CSV,WORLDCOVER_CLASSES,SOLAR_MULTIPLIER_BY_LANDCOVER




def find_landcover(tiles):
    df = pd.read_csv(GRID_POINTS_CSV)
    df["landcover_code"] = np.nan
 
    opened = [(t, rasterio.open(t)) for t in tiles]
 
    for idx, row in df.iterrows():
        lon, lat = row["lon"], row["lat"]
        for path, src in opened:
            left, bottom, right, top = src.bounds
            if left <= lon <= right and bottom <= lat <= top:
                val = next(src.sample([(lon, lat)]))[0]
                df.at[idx, "landcover_code"] = val
                break
        else:
            print(f"WARNING: point ({lat}, {lon}) not covered by any tile")
 
    for _, src in opened:
        src.close()
 
    return df
 
 
def sample_points():
    tiles = sorted(WORLDCOVER_TILES_DIR.glob("*.tif"))
    if not tiles:
        raise FileNotFoundError(f"No .tif files found in {WORLDCOVER_TILES_DIR}")
    print(f"Found {len(tiles)} tiles")
 
    df = find_landcover(tiles)
 
    df["land_type"] = df["landcover_code"].map(WORLDCOVER_CLASSES)
    df["solar_multiplier"] = df["landcover_code"].map(SOLAR_MULTIPLIER_BY_LANDCOVER)
 
    df.to_csv(LANDCOVER_CSV, index=False)
    print(f"Saved {len(df)} points -> {LANDCOVER_CSV}")
    print(df["land_type"].value_counts())
 
 
if __name__ == "__main__":
    LANDCOVER_CSV.parent.mkdir(parents=True, exist_ok=True)
    sample_points()
import rasterio
import pandas as pd
import numpy as np
from pathlib import Path

TILES_DIR = Path("../data/raw/MAP/")
GRID_CSV = Path("../data/processed/georgia_grid_points.csv")
OUTPUT_CSV = Path("../data/processed/georgia_grid_with_landtype.csv")


WORLDCOVER_CLASSES = {
    10: "Tree cover",
    20: "Shrubland",
    30: "Grassland",
    40: "Cropland",
    50: "Built-up",
    60: "Bare / sparse vegetation",
    70: "Snow and ice",
    80: "Permanent water bodies",
    90: "Herbaceous wetland",
    95: "Mangroves",
    100: "Moss and lichen",
    0: "No data",
}

SOLAR_MULTIPLIER = {
    10: 0.15,
    20: 0.25,
    30: 0.85,
    40: 0.80,
    50: 0.05,
    60: 0.95,
    70: 0.00,
    80: 0.00,
    90: 0.30,
    95: 0.05,
    100: 0.10,
    0: np.nan 
}

def find_landcover(tiles):
    df = pd.read_csv(GRID_CSV)
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
    tiles = sorted(TILES_DIR.glob("*.tif"))
    if not tiles:
        raise FileNotFoundError(f"No .tif files found in {TILES_DIR}")
    print(f"Found {len(tiles)} tiles")
 
    df = find_landcover(tiles)
 
    df["land_type"] = df["landcover_code"].map(WORLDCOVER_CLASSES)
    df["solar_multiplier"] = df["landcover_code"].map(SOLAR_MULTIPLIER)
 
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Saved {len(df)} points -> {OUTPUT_CSV}")
    print(df["land_type"].value_counts())
 
 
if __name__ == "__main__":
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    sample_points()
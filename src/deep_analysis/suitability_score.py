import rasterio
import numpy as np
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import IMPORT_SHARE_BY_MONTH,SYSTEM_LOSS_FACTOR



grid_scores = [0.9107646826946059,0.9409977195055086,0.8845710611120723]
solar_multiplier = [0.8,0.8,0.85]
for i in range(1,4):
    profile = None
    score_sum = None
    profile = None
    for j in range(1,13):
        import_share = IMPORT_SHARE_BY_MONTH.get(j, 0)
        if import_share == 0:
            continue
        with rasterio.open(f"../data/raw/deep_analysis/site_{i}_adjusted_irradiance_{j}.tif") as src:
            data = src.read(1,masked=True)
            if profile is None:
                profile = src.profile.copy()

            suitability_score = data*import_share*grid_scores[i-1]*solar_multiplier[i-1]*SYSTEM_LOSS_FACTOR
            print(suitability_score)
        if score_sum is None:
            score_sum = np.ma.zeros(data.shape, dtype=np.float32)
            score_sum.mask = data.mask.copy()

        score_sum += np.ma.filled(suitability_score, 0)

        print(score_sum)
    valid_values = score_sum.compressed()
    score_min = valid_values.min()
    score_max = valid_values.max()
    normal_score = (score_sum - score_min) / (score_max - score_min)
    normal_score = normal_score.astype(np.float32)
    profile.update(dtype="float32", count=1, nodata=-9999)
    output = f"../data/raw/deep_analysis/site_{i}_suitability_score.tif"
    with rasterio.open(output, "w", **profile) as dst:
        dst.write(normal_score.filled(-9999).astype("float32"), 1)

    

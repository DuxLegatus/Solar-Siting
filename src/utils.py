import csv
from config import GRID_POINTS_CSV,SYSTEM_LOSS_FACTOR


def get_grid_points():
    grid_points = []
    with open(GRID_POINTS_CSV, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            grid_points.append({"lat": float(row["lat"]), "lon": float(row["lon"])})
    return grid_points


def compute_suitability(df,solar_mutliplier=1,system_loss_multiplier=SYSTEM_LOSS_FACTOR):
    df = df.copy()
    df["import_weighted_contribution"] = (
        df["adjusted_irradiance"]
        * df["import_percentage"]
        * (df["solar_multiplier"] * solar_mutliplier)
        * df["protected_multiplier"]
        * system_loss_multiplier
    ).round(2)

    result = (
        df.groupby(["latitude", "longitude"], as_index=False)["import_weighted_contribution"]
        .sum()
        .rename(columns={"import_weighted_contribution": "suitability_score"})
    )
    return result

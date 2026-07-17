import pandas as pd
from config import SUITABILITY_CSV

def top10_set(df):
    top10 = df.nlargest(10, "suitability_score")
    return set(top10.apply(lambda r: (r["latitude"], r["longitude"]), axis=1))

baseline = pd.read_csv(SUITABILITY_CSV)
baseline_top10 = top10_set(baseline)
scenarios = [
    "georgia_suitability_scenario_1",
    "georgia_suitability_scenario_2",
    "georgia_suitability_scenario_3",
    "georgia_suitability_scenario_4",
    "georgia_suitability_scenario_5",
    "georgia_suitability_scenario_6",
]
results = []

for scenario in scenarios:
    df = pd.read_csv(f"../data/processed/{scenario}.csv")

    diff = df["suitability_score"] - baseline["suitability_score"]
    overlap = len(top10_set(df) & baseline_top10)
    results.append({
        "Scenario": scenario,
        "Mean Change": diff.mean(),
        "Mean Absolute Change": diff.abs().mean(),
        "Std Change": diff.std(),
        "Min Change": diff.min(),
        "Max Change": diff.max(),
        "Cells Changed": (diff != 0).sum(),
        "Percent Changed": 100 * (diff != 0).mean(),
        "Top 10 Overlap": f"{overlap}/10",
    })

summary = pd.DataFrame(results)
print(summary)
summary.to_csv("../data/processed/sensitivity_analysis_summary.csv", index=False)
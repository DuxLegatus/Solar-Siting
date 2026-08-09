import pandas

sites = pandas.read_csv("../data/processed/deep_analysis/terrain_analysis.csv").round(3).to_dict(orient="index")
import csv
import pandas as pd
import os

data = pd.read_csv("../data/processed/solar_irradiance_processed.csv")
data["month"] = data["year_month"].astype(str).str[4:6]
df = data.groupby(['latitude', 'longitude', 'month'])['irradiance'].mean().round(2).reset_index()
df.to_csv('../data/processed/solar_irradiance_monthly_avg.csv')
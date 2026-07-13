import csv
import pandas as pd
import os
from config import NASA_POWER_RAW_CSV,NASA_POWER_MONTHLY_AVG_CSV

data = pd.read_csv(NASA_POWER_RAW_CSV)
data["month"] = data["year_month"].astype(str).str[4:6]
df = data.groupby(['latitude', 'longitude', 'month'])['irradiance'].mean().round(2).reset_index()
df.to_csv(NASA_POWER_MONTHLY_AVG_CSV,index=False)
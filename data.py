from sklearn.linear_model import LinearRegression
import pandas as pd
from datetime import datetime

data = {
    "commissioning_date": ["2020-01-01", "2021-03-15", "2019-07-20", "2022-05-10"],
    "usage_frequency": [10, 20, 15, 25],  
    "failure_date": ["2022-01-01", "2023-03-15", "2021-07-20", "2024-05-10"]
}

df = pd.DataFrame(data)

df["commissioning_date"] = pd.to_datetime(df["commissioning_date"])
df["failure_date"] = pd.to_datetime(df["failure_date"])
df["days_until_failure"] = (df["failure_date"] - df["commissioning_date"]).dt.days

X = df[["usage_frequency"]]
y = df["days_until_failure"]
model = LinearRegression()
model.fit(X, y)
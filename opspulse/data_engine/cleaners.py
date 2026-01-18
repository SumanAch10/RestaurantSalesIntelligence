# fixes datatypes, missing values, currency strings, dates
from pathlib import Path
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
CSV_PATH = BASE_DIR/"restaurant_sales.csv"

def read_csv():
    df_raw = pd.read_csv(CSV_PATH)
    return df_raw

def all_ids(df_raw):
    bad_ids = df_raw.groupby("order_key")["customer_id"].nunique().loc[lambda s:s > 1].index
    good_ids = df_raw.groupby("order_key")["customer_id"].nunique().loc[lambda s:s == 1].index
    return bad_ids,good_ids

def split_dataframe(df_raw,bad_ids,good_ids):
    if(len(bad_ids)>0):
        print("inside the if statement")
        bad_data = df_raw[df_raw["order_key"].isin(bad_ids)].copy()
        bad_data.to_csv("bad_data.csv",index = False) #if bad data exists make a copy into a bad_data.csv
        good_data = df_raw[df_raw["order_key"].isin(good_ids)].copy() # and then rest of the data into original file
        good_data.to_csv(CSV_PATH,index = False)
        
df_raw = read_csv()
df_raw["order_key"] = df_raw["store_id"].astype(str) + "-" + df_raw["order_id"].astype(str)
print(df_raw)
bad_ids,good_ids = all_ids(df_raw)
print(bad_ids)
split_dataframe(df_raw,bad_ids,good_ids)
df_raw = read_csv()


# Import necessary libraries
import pandas as pd
import numpy as np
import glob
import os
from datetime import datetime, timedelta
import re

# Load data for Brazilian stocks (açao br e fii)
try:
    os.listdir("../input")
    path_input = "../input"
except:
    os.listdir("./input")
    path_input = "./input"
try:
    os.listdir("../data")
    path_data = "../data"
except:
    os.listdir("./data")
    path_data = "./data"


df_acfi = pd.read_excel(f"{path_input}/pat.xlsx", sheet_name="AçoesFII")
df_acfi = df_acfi.rename({"DATA": "date", "ITEM": "stock"}, axis=1)
df_acfi["date"] = pd.to_datetime(df_acfi["date"])
df_acfi = df_acfi.drop(["TAXA TOTAL"], axis=1)
df_acfi.columns = df_acfi.columns.str.lower()

# Load data for international stocks (açao de fora)
df_ac_int = pd.read_excel(f"{path_input}/pat.xlsx", sheet_name="Stocks")
df_ac_int = df_ac_int.rename({"DATA": "date", "ITEM": "stock"}, axis=1)
df_ac_int["date"] = pd.to_datetime(df_ac_int["date"])
df_ac_int.columns = df_ac_int.columns.str.lower()

# Load data for foreign currencies
df_usd = pd.read_csv(f"{path_data}/downloaded/data_bench_cur/currencies_historical_data.csv", sep=",")

# Clean up foreign currency data
df_usd = df_usd.drop(["EUR_bid", "EUR_ask", "index"], axis=1).rename(
    {"USD_bid": "USD_compra", "USD_ask": "USD_venda", "ITEM": "stock"}, axis=1
)[2:]
df_usd["Date"] = pd.to_datetime(df_usd["Date"])
df_usd.columns = df_usd.columns.str.lower()
df_usd["month"] = df_usd["date"].dt.month
df_usd["year"] = df_usd["date"].dt.year

# Display the loaded data for foreign currencies
df_usd

# Display the head of Brazilian stocks and international stocks dataframes
df_acfi.head(), df_ac_int.head()

# Process international stocks data
df_ac_int["preço médio"] = df_ac_int["preço médio_usd"] * df_ac_int["cambio_venda"]
df_ac_int["total"] = df_ac_int["total_usd"] * df_ac_int["cambio_venda"]
df_ac_int = df_ac_int.drop(["preço médio_usd", "total_usd", "cambio_venda"], axis=1)

# Concatenate Brazilian and international stocks data, and sort by date
df_variavel = pd.concat([df_acfi, df_ac_int]).sort_values("date")
df_variavel['date'] = pd.to_datetime(df_variavel['date'])

# Save the concatenated dataframe to CSV
df_variavel = df_variavel.reset_index(drop=True)
df_variavel.to_csv(f"{path_data}/Consolidado/df_ativos_mf.csv", sep=",", index=False)
df_variavel

# Load historical stock data from CSV files
path = f"{path_data}/downloaded/data_variavel"
all_files = glob.glob(path + "/*.csv")
dfs = []

for filename in all_files:
    stock_name = os.path.basename(filename).split("_")[0]
    df = pd.read_csv(filename)
    df["stock"] = stock_name
    df["Close"] = df["Close"].replace(0, method="ffill")
    dfs.append(df)

# Concatenate all historical stock dataframes
df_historico = pd.concat(dfs, ignore_index=True)
df_historico = df_historico.rename({"Date": "date", "Close": "close", "Dividends": "dividends", "Industry": "industry"}, axis=1)
df_historico['date'] = pd.to_datetime(df_historico['date'])
df_historico = df_historico[["date", "close", "dividends", "stock","industry"]]
df_historico["month"] = df_historico["date"].dt.month
df_historico["year"] = df_historico["date"].dt.year

#df_historico.loc[df_historico["industry"].isna(),"industry"] = df_historico.loc[df_historico["industry"].isna()]["tipo"]


# Set the values for rows where 'dividends' is greater than 0
df_historico['date_dividends_payed'] = df_historico.loc[df_historico['dividends'] > 0, 'date']
df_historico['date_dividends_payed'] = df_historico.groupby(['stock', 'month', 'year'])['date_dividends_payed'].transform('last')

# Sort DataFrame by 'stock' and 'date'
df_historico.sort_values(by=['stock', 'date'], inplace=True)
df_historico["cumsum_dividendos"] = df_historico.groupby(['stock', 'month', 'year']).agg(
    dividends=pd.NamedAgg(column="dividends", aggfunc="cumsum")
)
df_historico

# Generate a date range from January 2020 to today
start_date = datetime(2020, 1, 1)
end_date = datetime.now().date()
date_range = pd.date_range(start=start_date, end=end_date, freq='d')

# Create a DataFrame with 'Month' and 'Year' columns
df_datas = pd.DataFrame({'date': date_range})

# Merge all dataframes
df_all_stocks = pd.concat([df_acfi, df_ac_int], ignore_index=True)
df_port = pd.merge(df_datas, df_historico.drop(["month", "year"], axis=1), how="left", on=["date"])
df_port = pd.merge(df_port, df_usd.drop(["month", "year"], axis=1), how="left", on=["date"])
df_port["month"] = df_port["date"].dt.month
df_port["year"] = df_port["date"].dt.year

# Forward-fill missing values for USD exchange rates
df_port["usd_compra"] = df_port["usd_compra"].ffill()
df_port["usd_venda"] = df_port["usd_venda"].ffill()

# Save the final dataframe to CSV
df_port.to_csv(f"{path_data}/Consolidado/df_historico_total.csv", sep=",", index=False)

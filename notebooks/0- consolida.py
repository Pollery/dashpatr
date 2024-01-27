# Import necessary libraries
import pandas as pd
import numpy as np
import os
import requests


##AJUSTAR
LOCAL_SENHAS_GITHUB = 'G:\\Projetinhos\\Patrimonio'

# Read stock-related data from Excel sheets
try:
    df_acfi = pd.read_excel("../input/pat.xlsx", sheet_name="AçoesFII")
except FileNotFoundError:
    df_acfi = pd.read_excel("./input/pat.xlsx", sheet_name="AçoesFII")
try:
    df_ac_int = pd.read_excel("../input/pat.xlsx", sheet_name="Stocks")
except FileNotFoundError:
    df_ac_int = pd.read_excel("./input/pat.xlsx", sheet_name="Stocks")
try:
    df_banco = pd.read_excel("../input/pat.xlsx", sheet_name="Bancos")
except FileNotFoundError:
    df_banco = pd.read_excel("./input/pat.xlsx", sheet_name="Bancos")

# Read Nubank account statements from CSV files in a specified directory
try:
    os.listdir("../input/Extrato Conta")
    directory_path = "../input/Extrato Conta"
except:
    os.listdir("./input/Extrato Conta")
    directory_path = "./input/Extrato Conta"

df_extrato = pd.DataFrame()
for filename in os.listdir(directory_path):
    if filename.endswith(".csv"):
        file_path = os.path.join(directory_path, filename)
        df = pd.read_csv(file_path)
        df_extrato = pd.concat([df_extrato, df], ignore_index=True)

# Process and consolidate Nubank account statements
df_extrato["Data"] = pd.to_datetime(df_extrato["Data"], format="%d/%m/%Y")
df_extrato = df_extrato.sort_values("Data")
df_extrato_consolidado = df_extrato.copy()
df_extrato_consolidado["tipo"] = (
    df_extrato_consolidado["Descrição"].str.split("-").str.get(0) +
    " - " +
    df_extrato_consolidado["Descrição"].str.split("-").str.get(1)
)
df_extrato_consolidado["title"] = df_extrato_consolidado["tipo"].fillna(df_extrato["Descrição"])
df_extrato_consolidado["pessoa"] = (
    df_extrato_consolidado["Descrição"].str.split("-").str.get(1)
)
try:
    df_extrato_consolidado.to_csv(
    "../data/consolidado/df_extrato_consolidado.csv", index=False, sep=","
)
except:
    df_extrato_consolidado.to_csv(
    "./data/consolidado/df_extrato_consolidado.csv", index=False, sep=","
)
# Read Nubank investment returns from CSV files
try:
    os.listdir("../input/rendimento nubank")
    directory_path = "../input/rendimento nubank"
except:
    os.listdir("./input/rendimento nubank")
    directory_path = "./input/rendimento nubank"

df_rendimento = pd.DataFrame()
for filename in os.listdir(directory_path):
    if filename.endswith(".csv"):
        file_path = os.path.join(directory_path, filename)
        df = pd.read_csv(file_path)
        df_rendimento = pd.concat([df_rendimento, df], ignore_index=True)

# Process and consolidate investment returns
df_rendimento = df_rendimento.sort_values("Data")
try:
    df_rendimento.to_csv("../data/consolidado/df_rendimento.csv", index=False, sep=",")
except:
    df_rendimento.to_csv("./data/consolidado/df_rendimento.csv", index=False, sep=",")

# Read Nubank credit card statements from CSV files
try:
    os.listdir("../input/Faturas/NU")
    directory_path = "../input/Faturas/NU"
except:
    os.listdir("./input/Faturas/NU")
    directory_path = "./input/Faturas/NU"

df_faturas_nu = pd.DataFrame()
for filename in os.listdir(directory_path):
    if filename.endswith(".csv"):
        file_path = os.path.join(directory_path, filename)
        df = pd.read_csv(file_path)
        df_faturas_nu = pd.concat([df_faturas_nu, df], ignore_index=True)

# Process and consolidate Nubank credit card statements
df_faturas_nu["date"] = pd.to_datetime(df_faturas_nu["date"], format="%Y-%m-%d", errors="coerce")
df_faturas_nu = df_faturas_nu.sort_values("date").reset_index(drop=True)
df_faturas_nu["amount"] = pd.to_numeric(df_faturas_nu["amount"], errors="coerce")
df_faturas_nu["Estabelecimento"] = df_faturas_nu["title"]
df_faturas_nu["IF"] = "NU"
df_faturas_nu["Portador"] = "MARCOS POLLERY"
extracted_title = df_faturas_nu["Estabelecimento"].str.extract(r"\*(.*?)\s*(\d+/\d+|$)").get(0)
df_faturas_nu["title"] = extracted_title.fillna(df_faturas_nu["Estabelecimento"])
df_faturas_nu["Parcela"] = df_faturas_nu["Estabelecimento"].str.extract(r"(\d+/\d+)$").replace("/", " de ", regex=True)
try:
    df_faturas_nu.to_csv("../data/consolidado/df_faturas_nu.csv", index=False, sep=",")
except:
    df_faturas_nu.to_csv("./data/consolidado/df_faturas_nu.csv", index=False, sep=",")

# Read XP credit card statements from CSV files
try:
    os.listdir("../input/Faturas/XP")
    directory_path = "../input/Faturas/XP"
except:
    os.listdir("./input/Faturas/XP")
    directory_path = "./input/Faturas/XP"  


df_faturas_xp = pd.DataFrame()
for filename in os.listdir(directory_path):
    if filename.endswith(".csv"):
        file_path = os.path.join(directory_path, filename)
        df = pd.read_csv(file_path, sep=";")
        df_faturas_xp = pd.concat([df_faturas_xp, df], ignore_index=True)

# Process and consolidate XP credit card statements
df_faturas_xp["Data"] = pd.to_datetime(df_faturas_xp["Data"], format="%d/%m/%Y", errors="coerce")
df_faturas_xp = df_faturas_xp.sort_values("Data").reset_index(drop=True)
df_faturas_xp["Valor"] = (
    pd.to_numeric(df_faturas_xp["Valor"].replace("[^\\d.]", "", regex=True).str.replace(",", "."), errors="coerce") / 100
)
df_faturas_xp["title"] = df_faturas_xp["Estabelecimento"].str.split("*").str.get(-1)
df_faturas_xp = df_faturas_xp.rename({"Data": "date", "Valor": "amount"}, axis=1)
df_faturas_xp["category"] = np.nan
df_faturas_xp["IF"] = "XP"
df_faturas_xp["Parcela"] = df_faturas_xp["Parcela"].replace("-", np.nan)
try:
    df_faturas_xp.to_csv("../data/consolidado/df_faturas_xp.csv", index=False, sep=",")
except:
    df_faturas_xp.to_csv("./data/consolidado/df_faturas_xp.csv", index=False, sep=",")

# Combine and process all credit card statements
df_faturas = pd.concat([
    df_faturas_nu.loc[~df_faturas_nu["Estabelecimento"].str.contains("Pagamento recebido")],
    df_faturas_xp
]).sort_values("date")

# Adjust XP credit card statement dates to match Nubank
df_faturas["date2"] = df_faturas["date"]
xp_rows = df_faturas[df_faturas["IF"] == "XP"]
first_items = pd.to_numeric(xp_rows["Parcela"].str.split("de").str[0], errors="coerce")
condition = first_items > 1
for index, value in first_items[condition].items():
    df_faturas.at[index, "date"] += pd.DateOffset(months=int(value) - 1)

df_faturas.sort_values("date")

try:
    df_faturas.to_csv("../data/consolidado/df_faturas.csv", index=False, sep=",")
except:
    df_faturas.to_csv("./data/consolidado/df_faturas.csv", index=False, sep=",")
# Download files from GitHub repositories
import os
import requests

import sys
sys.path.append(LOCAL_SENHAS_GITHUB)
from load_data.password import *

for folder_path in folder_paths:
    api_url = f"https://api.github.com/repos/{github_username}/{github_repo}/contents/{folder_path}"
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        files = response.json()
        try:
            os.listdir(f"../data/downloaded/{folder_path.replace('/', '_')}")
            local_directory =f"../data/downloaded/{folder_path.replace('/', '_')}"
        except:
            os.listdir(f"./data/downloaded/{folder_path.replace('/', '_')}")
            local_directory = f"./data/downloaded/{folder_path.replace('/', '_')}"

        os.makedirs(local_directory, exist_ok=True)

        for file_info in files:
            file_name = os.path.basename(file_info["name"])
            if file_name.endswith("_historical_data.csv"):
                raw_url = file_info["download_url"]
                file_response = requests.get(raw_url, headers=headers)

                if file_response.status_code == 200:
                    local_path = os.path.join(local_directory, file_name)
                    with open(local_path, "wb") as local_file:
                        local_file.write(file_response.content)
                    print(f"Downloaded: {file_name}")
                else:
                    print(f"Failed to download file: {file_name}")
    else:
        print(f"Failed to retrieve folder contents for {folder_path}. Status code: {response.status_code}")

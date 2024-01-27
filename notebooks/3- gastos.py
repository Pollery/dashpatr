# Import necessary libraries
import pandas as pd
import numpy as np

# Read the consolidated invoice data
try:
    df_faturas = pd.read_csv("../data/consolidado/df_faturas.csv")
except FileNotFoundError:
    df_faturas = pd.read_csv("./data/consolidado/df_faturas.csv")
    # Handle the file not found exception here

# Drop unnecessary column "date2"
df_faturas = df_faturas.drop(["date2"], axis=1)

# Read the consolidated statement data
try:
    df_extrato = pd.read_csv("./data/consolidado/df_extrato_consolidado.csv")
except FileNotFoundError:
    df_extrato = pd.read_csv("../data/consolidado/df_extrato_consolidado.csv")
    # Handle the file not found exception here

df_extrato

# Rename columns for consistency
df_extrato = df_extrato.rename({"Data": "date",  "Valor": "amount"}, axis=1)

# Reverse the sign of the amounts in the statement
df_extrato["amount"] = df_extrato["amount"] * -1

# Adjust columns for identification and merging with the invoice data
df_extrato["pessoa"] = df_extrato["pessoa"].fillna("")
df_extrato["Estabelecimento"] = df_extrato["Descrição"]
df_extrato["IF"] = "NUCONTA"
df_extrato["Parcela"] = np.nan
df_extrato["category"] = np.nan
df_extrato["Portador"] = "Marcos Pollery"
df_extrato = df_extrato.drop(["Identificador", "Descrição"], axis=1)



# Exclude specific transactions from the statement
df_extrato = df_extrato[~(df_extrato["pessoa"].str.lower().str.contains("marcos") &
                         df_extrato["pessoa"].str.lower().str.contains("pollery"))]
df_extrato = df_extrato[~(df_extrato["title"].fillna("").str.lower().str.contains("fatura"))]
df_extrato = df_extrato[~(df_extrato["title"].str.lower().str.contains("aplicação rdb"))]
df_extrato = df_extrato[~(df_extrato["title"].str.lower().str.contains("resgate rdb"))]
df_extrato = df_extrato[~(df_extrato["title"].str.lower().str.contains("pedacinho"))]
df_extrato = df_extrato[~(df_extrato["title"].str.lower().str.contains("crédito em conta"))]
df_extrato = df_extrato[~(df_extrato["title"].str.lower().str.contains("resgate planejado"))]
df_extrato = df_extrato[~(df_extrato["Estabelecimento"].str.lower().str.contains("07.679.404/0001-00"))]
df_extrato = df_extrato[~(df_extrato["Estabelecimento"].str.lower().str.contains("pagamento de boleto efetuado - banco xp s/a"))]

# Exclude specific transactions from the invoice data
df_faturas = df_faturas[~(df_faturas["title"].str.lower().str.contains("pagamentos validos normais"))]



# Drop the "pessoa" column from the statement data
df_extrato = df_extrato.drop(["pessoa"], axis=1)

# Convert date columns to datetime format
df_faturas["date"] = pd.to_datetime(df_faturas["date"], format="%Y-%m-%d")

df_extrato["date"] = pd.to_datetime(df_extrato["date"], format="%Y-%m-%d")


# Display the last few rows of the invoice data
df_faturas.tail()

# Extract month and year from the date columns
df_faturas["Month"] = df_faturas["date"].dt.month
df_faturas["Year"] = df_faturas["date"].dt.year
df_extrato["Month"] = df_extrato["date"].dt.month
df_extrato["Year"] = df_extrato["date"].dt.year

# Concatenate the invoice and statement data and sort by date
expenses = pd.concat([df_faturas, df_extrato]).sort_values("date")
expenses.sample(10)

# Save the consolidated data to a CSV file
try:
    expenses.to_csv("./data/consolidado/gastos_fatura_extrato.csv", index=False, sep=",")
except:
    expenses.to_csv("../data/consolidado/gastos_fatura_extrato.csv", index=False, sep=",")


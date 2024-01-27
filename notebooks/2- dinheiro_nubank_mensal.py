# Importing necessary libraries
import os
import pandas as pd

# Load data for Brazilian stocks (ação br e fii)
try:
    os.listdir("../data")
    path_input = "../data"
except:
    os.listdir("./data")
    path_input = "./data"

# Reading the data from the CSV file
df_rendimento = pd.read_csv(f"{path_input}/consolidado/df_rendimento.csv")

# Converting the "Data" column to datetime format
df_rendimento['Data'] = pd.to_datetime(df_rendimento['Data'])

# Extracting month and year information from the "Data" column
df_rendimento['Month'] = df_rendimento['Data'].dt.month
df_rendimento['Year'] = df_rendimento['Data'].dt.year

# Grouping by year and month, and summing the values
monthly_sum = df_rendimento.groupby(['Year', 'Month']).agg({
    'Entradas': 'sum',
    'Saídas': 'sum',
    'IR': 'sum',
    'IOF': 'sum',
    'Rendimentos': 'sum'
}).reset_index()

# Creating a mask to select the last row of each month
mask = df_rendimento.groupby(['Year', 'Month'])['Data'].transform('max') == df_rendimento['Data']

# Using the mask to select the last row of each month
last_rows_of_each_month = df_rendimento[mask]

# Merging the last row information with the monthly sum
result = pd.merge(last_rows_of_each_month, monthly_sum, on=['Year', 'Month'], suffixes=('_last_row', '_monthly_sum'))

# Dropping unnecessary columns from the result
result = result.drop(["Entradas_last_row", "Saídas_last_row", "IR_last_row", "IOF_last_row", "Rendimentos_last_row"], axis=1)

# Saving the result to a CSV file
result.to_csv(f"{path_input}/consolidado/movimentação_bancaria_mensal.csv", index=False, sep=",")

import numpy as np
from datetime import datetime, timedelta
import datetime
import pandas as pd





### Gastos
month_mapping = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Março",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro",
}

try:
    spend_data = pd.read_csv("./data/consolidado/gastos_fatura_extrato.csv", sep=",")
except FileNotFoundError:
    # Handle the case where the first file path is not found
    spend_data = pd.read_csv("../data/consolidado/gastos_fatura_extrato.csv", sep=",")


spend_data = spend_data.rename(
    {
        "amount": "Amount",
        "title": "Category",
        "date": "Date",
        "IF": "Account",
    },
    axis=1,
)
spend_data["Date"] = pd.to_datetime(spend_data["Date"], format="%Y-%m-%d")


spend_data["Pretty_Month"] = spend_data["Month"].map(month_mapping)


try:
    spend_data.to_parquet("../data/Final/spend_data.gzip",index=False)
except:
    spend_data.to_parquet("./data/Final/spend_data.gzip",index=False)







### Investimentos Networth

#benchmarks
    
try:
    # Try to read the CSV file using relative path
    df_usd = pd.read_csv("../data/downloaded/data_bench_cur/currencies_historical_data.csv")
except FileNotFoundError:
    # If the file is not found, read using an absolute path
    df_usd = pd.read_csv("./data/downloaded/data_bench_cur/currencies_historical_data.csv")

df_usd = df_usd.ffill()
df_usd = df_usd[["Date","USD_ask"]].rename({"USD_ask":"USD"},axis=1)
df_usd["Date"] = pd.to_datetime(df_usd["Date"], format="%Y-%m-%d")
df_usd["Date"] = df_usd["Date"].dt.to_period("M")


try:
    # Try to read the CSV file using relative path
    df_selic = pd.read_csv("../data/downloaded/data_bench_cur/selic_historical_data.csv")
except FileNotFoundError:
    # If the file is not found, read using an absolute path
    df_selic = pd.read_csv("./data/downloaded/data_bench_cur/selic_historical_data.csv")

df_selic = df_selic.ffill()
df_selic["Date"] = pd.to_datetime(df_selic["Date"], format="%Y-%m-%d")
df_selic["Date"] = df_selic["Date"].dt.to_period("M")

try:
    # Try to read the CSV file using relative path
    df_infla = pd.read_csv("../data/downloaded/data_bench_cur/inflacao_historical_data.csv")
except FileNotFoundError:
    # If the file is not found, read using an absolute path
    df_infla = pd.read_csv("./data/downloaded/data_bench_cur/inflacao_historical_data.csv")

df_infla = df_infla.ffill()
df_infla["Date"] = pd.to_datetime(df_infla["Date"], format="%Y-%m-%d")
df_infla["Date"] = df_infla["Date"].dt.to_period("M")







# le salário
try:
    df_salario = pd.read_excel("./input/pat.xlsx", sheet_name="Salário")
except FileNotFoundError:
    df_salario = pd.read_excel("../input/pat.xlsx", sheet_name="Salário")
try:
    df_salario.to_parquet("../data/Final/df_salario.gzip",index=False)
except:
    df_salario.to_parquet("./data/Final/df_salario.gzip",index=False)
# le data acoes (acoes que tenho)
try:
    data_acoes = pd.read_csv("./data/Consolidado/df_ativos_mf.csv", sep=",")
except FileNotFoundError:
    # Handle the case where the first file path is not found
    data_acoes = pd.read_csv("../data/Consolidado/df_ativos_mf.csv", sep=",")

data_acoes = data_acoes.rename(
    {"date": "Date_bought"},
    axis=1,
).drop("preço médio", axis=1)

# historico das acoes
try:
    df_historico = pd.read_csv("../data/Consolidado/df_historico_total.csv", sep=",")
except FileNotFoundError:
    # Handle the case where the first file path is not found
    df_historico = pd.read_csv("./data/Consolidado/df_historico_total.csv", sep=",")

# caixinha
try:
    df_caixinha = pd.read_excel("../input/pat.xlsx", sheet_name="Caixinha")
except FileNotFoundError:
    df_caixinha = pd.read_excel("./input/pat.xlsx", sheet_name="Caixinha")

try:
    df_caixinha.to_parquet("../data/Final/df_caixinha.gzip",index=False)
except:
    df_caixinha.to_parquet("./data/Final/df_caixinha.gzip",index=False)

df_historico = df_historico.rename(
    {"date": "Date"},
    axis=1,
)


df_historico["Date"] = pd.to_datetime(df_historico["Date"])

# fazendo ter a minha carteira todos os dias
# Create a DataFrame with all months between the min and max months
start_date = data_acoes["Date_bought"].min()
current_datetime = datetime.datetime.now()

     
end_date = current_datetime.date()

date_range = pd.date_range(start=start_date, end=end_date, freq="BM").append(
    pd.Index([end_date])
)



df_datas = pd.DataFrame(date_range).rename({0: "Date"}, axis=1)
df_datas["Date"] = pd.to_datetime(df_datas["Date"])
df_datas["Date"] = df_datas["Date"].dt.strftime("%Y-%m-%d")



df_datas_carteira = pd.DataFrame()
df_acoes = pd.DataFrame()

# calculando a carteira em cada data

for index, rows in df_datas.iterrows():
    df_acoes = data_acoes.loc[data_acoes["Date_bought"] <= rows["Date"]].copy()
    df_acoes["Date"] = rows["Date"]
    df_datas_carteira = pd.concat([df_datas_carteira, df_acoes])

df_datas_carteira = df_datas_carteira.reset_index(drop=True)
df_datas_carteira["Date"] = pd.to_datetime(df_datas_carteira["Date"])

# juntando a carteira com o historico
df_datas_carteira = pd.merge(
    df_datas_carteira,
    df_historico.drop(["month", "year"], axis=1),
    how="left",
    on=["Date", "stock"],
)



df_datas_carteira["Date"] = df_datas_carteira["Date"].dt.to_period("M")



# calculando valor das acoes internacionais

# Conditionally calculate the "actual_value" column
df_datas_carteira["actual_value_brl"] = np.where(
    df_datas_carteira["stock"].str.endswith(".L"),
    df_datas_carteira["qtd"]
    * df_datas_carteira["close"]
    * df_datas_carteira["usd_compra"],
    df_datas_carteira["qtd"] * df_datas_carteira["close"],
)

df_datas_carteira = df_datas_carteira.drop(["dividends"] , axis=1)

# Filter rows based on the condition
condition = df_datas_carteira["Date_bought"] < df_datas_carteira["date_dividends_payed"]
df_datas_carteira.loc[condition, "dividends"] = df_datas_carteira.loc[condition, "cumsum_dividendos"]
df_datas_carteira = df_datas_carteira.drop(['cumsum_dividendos'],axis=1)
#df_datas_carteira.loc[df_datas_carteira["industry"].isna(),"industry"] = df_datas_carteira.loc[df_datas_carteira["industry"].isna()]["tipo"]


try:
    df_datas_carteira.to_parquet("../data/Final/df_datas_carteira.gzip",index=False)
except:
    df_datas_carteira.to_parquet("./data/Final/df_datas_carteira.gzip",index=False)



df_datas_carteira_mensal_aberto = (
    df_datas_carteira.groupby(
        [
            "Date",
            "tipo",
            "stock",
        ]
    )[["industry","qtd", "total", "actual_value_brl", "dividends"]]
    .agg(
        qtd=pd.NamedAgg(column="qtd", aggfunc="sum"),
        total=pd.NamedAgg(column="total", aggfunc="sum"),
        actual_value_brl=pd.NamedAgg(column="actual_value_brl", aggfunc="sum"),
        dividends = pd.NamedAgg(column="dividends", aggfunc="max"),
        industry = pd.NamedAgg(column="dividends", aggfunc="last"),
    )
    .reset_index()
)

df_datas_carteira_mensal_aberto = pd.merge(df_datas_carteira_mensal_aberto, df_infla, how='left', on='Date')
df_datas_carteira_mensal_aberto = pd.merge(df_datas_carteira_mensal_aberto, df_usd, how='left', on='Date')
df_datas_carteira_mensal_aberto = pd.merge(df_datas_carteira_mensal_aberto, df_selic, how='left', on='Date')


# calculando impostos

df_datas_carteira_mensal_aberto["Lucro"] = df_datas_carteira_mensal_aberto["actual_value_brl"] - df_datas_carteira_mensal_aberto["total"]
df_datas_carteira_mensal_aberto["Lucro"] = np.maximum(df_datas_carteira_mensal_aberto["Lucro"], 0)
df_datas_carteira_mensal_aberto["Imposto"] = df_datas_carteira_mensal_aberto["Lucro"]*0.15
df_datas_carteira_mensal_aberto["Valor liq"] = df_datas_carteira_mensal_aberto["actual_value_brl"] - df_datas_carteira_mensal_aberto["Imposto"]

df_datas_carteira_mensal_aberto["dividends"] = df_datas_carteira_mensal_aberto["dividends"].fillna(0)
df_datas_carteira_mensal_aberto["dividends_total"] = df_datas_carteira_mensal_aberto["qtd"] * df_datas_carteira_mensal_aberto["dividends"]


try:
    df_datas_carteira_mensal_aberto.to_parquet("../data/Final/df_datas_carteira_mensal_aberto.gzip",index=False)
except:
    df_datas_carteira_mensal_aberto.to_parquet("./data/Final/df_datas_carteira_mensal_aberto.gzip",index=False)

df_datas_carteira_mensal = (
    df_datas_carteira.groupby(
        [
            "Date",
        ]
    )[["qtd", "total", "actual_value_brl", "dividends"]]
    .agg(
        qtd=pd.NamedAgg(column="qtd", aggfunc="sum"),
        total=pd.NamedAgg(column="total", aggfunc="sum"),
        actual_value_brl=pd.NamedAgg(column="actual_value_brl", aggfunc="sum"),
        dividends=pd.NamedAgg(column="dividends", aggfunc="sum")
    )
    .reset_index()
)


df_datas_carteira_mensal = pd.merge(df_datas_carteira_mensal, df_infla, how='left', on='Date')
df_datas_carteira_mensal = pd.merge(df_datas_carteira_mensal, df_usd, how='left', on='Date')
df_datas_carteira_mensal = pd.merge(df_datas_carteira_mensal, df_selic, how='left', on='Date')


# calculando impostos

df_datas_carteira_mensal["Lucro"] = df_datas_carteira_mensal["actual_value_brl"] - df_datas_carteira_mensal["total"]
df_datas_carteira_mensal["Lucro"] = np.maximum(df_datas_carteira_mensal["Lucro"], 0)
df_datas_carteira_mensal["Imposto"] = df_datas_carteira_mensal["Lucro"]*0.15
df_datas_carteira_mensal["Valor liq"] = df_datas_carteira_mensal["actual_value_brl"] - df_datas_carteira_mensal["Imposto"]

df_datas_carteira_mensal["dividends"] = df_datas_carteira_mensal["dividends"].fillna(0)
df_datas_carteira_mensal["dividends_total"] = df_datas_carteira_mensal["qtd"] * df_datas_carteira_mensal["dividends"]

try:
    df_datas_carteira_mensal.to_parquet("../data/Final/df_datas_carteira_mensal.gzip",index=False)
except:
    df_datas_carteira_mensal.to_parquet("./data/Final/df_datas_carteira_mensal.gzip",index=False)


# historico conta nubank

try:
    data_conta = pd.read_csv("./data/Consolidado/df_rendimento.csv", sep=",")
except FileNotFoundError:
    # Handle the case where the first file path is not found
    data_conta = pd.read_csv("../data/Consolidado/df_rendimento.csv", sep=",")

data_conta = data_conta.rename(
    {
        "Data": "Date",
    },
    axis=1,
)

data_conta["Date"] = pd.to_datetime(data_conta["Date"], format="%Y-%m-%d")

try:
    data_conta.to_parquet("../data/Final/data_conta.gzip",index=False)
except:
    data_conta.to_parquet("./data/Final/data_conta.gzip",index=False)

# arrumando para calculos mensais

data_conta_mensal = data_conta.groupby(data_conta["Date"].dt.to_period("M"))[
    ["IOF", "Entradas", "Saídas", "IR", "Rendimentos", "Saldo Líquido"]
].agg(
    Entradas=pd.NamedAgg(column="Entradas", aggfunc="sum"),
    Saídas=pd.NamedAgg(column="Saídas", aggfunc="sum"),
    IOF=pd.NamedAgg(column="IOF", aggfunc="sum"),
    IR=pd.NamedAgg(column="IR", aggfunc="sum"),
    Rendimentos=pd.NamedAgg(column="Rendimentos", aggfunc="sum"),
    SaldoLíquido=pd.NamedAgg(column="Saldo Líquido", aggfunc="last"),
)
data_conta_mensal = data_conta_mensal.reset_index()

try:
    data_conta_mensal.to_parquet("../data/Final/data_conta_mensal.gzip",index=False)
except:
    data_conta_mensal.to_parquet("./data/Final/data_conta_mensal.gzip",index=False)




df_datas_carteira_mensal_aberto.loc[
    df_datas_carteira_mensal_aberto["stock"].str.contains("VWRA"), "industry"
] = "Global"

df_datas_carteira_mensal_aberto.loc[
    df_datas_carteira_mensal_aberto["stock"].str.contains("EIMI"), "industry"
] = "Global Small"

df_datas_carteira_mensal_aberto.loc[
    df_datas_carteira_mensal_aberto["stock"].str.contains("BOVA"), "industry"
] = "Brasil Bova"

df_datas_carteira_mensal_aberto.loc[
    df_datas_carteira_mensal_aberto["stock"].str.contains("SMAL"), "industry"
] = "Brasil Small"

df_datas_carteira_mensal_aberto.loc[
    df_datas_carteira_mensal_aberto["stock"].str.contains("ITIT"), "industry"
] = "FOF Tijolo"

# Process yearly investment data
df_datas_carteira_mensal_aberto["year"] = df_datas_carteira_mensal_aberto["Date"].dt.year

df_datas_carteira_anual_aberto = df_datas_carteira_mensal_aberto.groupby(
    ["year", "tipo", "industry", "stock"]
).agg(
    aporte=pd.NamedAgg(column="total", aggfunc="last"),
    actual_value_brl=pd.NamedAgg(column="actual_value_brl", aggfunc="last"),
    Lucro=pd.NamedAgg(column="Lucro", aggfunc="last"),
    Imposto=pd.NamedAgg(column="Imposto", aggfunc="last"),
    dividends_total=pd.NamedAgg(column="dividends_total", aggfunc="last"),
    Valor_liq=pd.NamedAgg(column="Valor liq", aggfunc="last"),
    ipca =pd.NamedAgg(column="ipca", aggfunc="last"),
    igp_m =pd.NamedAgg(column="igp-m", aggfunc="last"),
    USD =pd.NamedAgg(column="USD", aggfunc="last"),
    selic =pd.NamedAgg(column="selic", aggfunc="last"),
)
df_datas_carteira_anual_aberto = df_datas_carteira_anual_aberto.reset_index()

# Calculate percentage of actual_value_brl for all years
df_datas_carteira_anual_aberto["total_anual"] = df_datas_carteira_anual_aberto.groupby(
    "year"
)["actual_value_brl"].transform("sum")
df_datas_carteira_anual_aberto["pct_actual_value_brl"] = round(
    (
        df_datas_carteira_anual_aberto["actual_value_brl"]
        / df_datas_carteira_anual_aberto["total_anual"]
        * 100
    ),
    2,
)
df_datas_carteira_anual_aberto["Lucro_Loss"] = (
    df_datas_carteira_anual_aberto["actual_value_brl"]
    - df_datas_carteira_anual_aberto["aporte"]
)
df_datas_carteira_anual_aberto["Lucro_Dividendos"] = (
    (
        df_datas_carteira_anual_aberto["Lucro_Loss"]
        + df_datas_carteira_anual_aberto["dividends_total"]
    )
    / df_datas_carteira_anual_aberto["aporte"]
    * 100
)

df_datas_carteira_anual_aberto


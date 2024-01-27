import pandas as pd
import plotly.express as px
import streamlit as st
import numpy as np
from datetime import datetime, timedelta
import datetime




# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title="Networth", page_icon=":bar_chart:", layout="wide")

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)



try:
    df_datas_carteira_mensal = pd.read_parquet("../data/Final/df_datas_carteira_mensal.gzip")
except FileNotFoundError:
    df_datas_carteira_mensal = pd.read_parquet("./data/Final/df_datas_carteira_mensal.gzip")

try:
    data_conta_mensal = pd.read_parquet("../data/Final/data_conta_mensal.gzip")
except FileNotFoundError:
    data_conta_mensal = pd.read_parquet("./data/Final/data_conta_mensal.gzip")

try:
    data_conta = pd.read_parquet("../data/Final/data_conta.gzip")
except FileNotFoundError:
    data_conta = pd.read_parquet("./data/Final/data_conta.gzip")


try:
    df_caixinha = pd.read_parquet("../data/Final/df_caixinha.gzip")
except FileNotFoundError:
    df_caixinha = pd.read_parquet("./data/Final/df_caixinha.gzip")


##df_datas_carteira_mensal , data_conta_mensal , df_datas_carteira_mensal_aberto
networth_anterior = (
    df_datas_carteira_mensal[-2:]["Valor liq"].values
    + data_conta_mensal[-2:]["SaldoLíquido"].values
)
networth_anterior = networth_anterior[0]
networth = (
    df_datas_carteira_mensal[-1:]["Valor liq"].values
    + data_conta_mensal[-1:]["SaldoLíquido"].values
)
networth = networth[0]

networth_str_liq = "R${:,.2f}".format(networth)

networth_change = networth - networth_anterior 

df_networth = pd.merge(df_datas_carteira_mensal[["Date","actual_value_brl"]],data_conta_mensal[["Date","SaldoLíquido"]].reset_index(),how="outer",on="Date").fillna(0).drop("index",axis=1)
df_networth["net_worth"] = df_networth["actual_value_brl"]+df_networth["SaldoLíquido"]
df_networth['Current Month'] = df_networth['Date'].dt.strftime('%B %Y')
df_networth['Current Month'] = df_networth['Current Month'].astype(str)
df_networth = df_networth.sort_values("Date")

net_worth_chart_df = df_networth
net_worth_chart_df.rename(columns={"Current Month": "Month"}, inplace=True)
net_worth_chart_df.rename(
    columns={'net_worth': "Net Worth"}, inplace=True
)

df_networth_liq = pd.merge(df_datas_carteira_mensal[["Date","Valor liq"]],data_conta_mensal[["Date","SaldoLíquido"]].reset_index(),how="outer",on="Date").fillna(0).drop("index",axis=1)
df_networth_liq["net_worth"] = df_networth_liq["Valor liq"]+df_networth["SaldoLíquido"]
df_networth_liq['Current Month'] = df_networth_liq['Date'].dt.strftime('%B %Y')
df_networth_liq['Current Month'] = df_networth_liq['Current Month'].astype(str)
df_networth_liq = df_networth_liq.sort_values("Date")

net_worth_chart_df_liq = df_networth_liq
net_worth_chart_df_liq.rename(columns={"Current Month": "Month"}, inplace=True)
net_worth_chart_df_liq.rename(
    columns={'net_worth': "Net Worth"}, inplace=True
)

# NET WORTH CHART
fig_net_worth = px.area(
    net_worth_chart_df["Net Worth"],
    x=net_worth_chart_df.Month,
    y="Net Worth",
    title="",
    color_discrete_sequence=["#0083B8"] * len(net_worth_chart_df),
    template="plotly_white",
)
fig_net_worth.update_layout(
    xaxis=dict(tickmode="linear"),
    xaxis_title="Month",
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=(dict(showgrid=False)),
)

# NET WORTH CHART LIQUIDO
fig_net_worth_liq = px.area(
    net_worth_chart_df_liq["Net Worth"],
    x=net_worth_chart_df.Month,
    y="Net Worth",
    title="",
    color_discrete_sequence=["#0083B8"] * len(net_worth_chart_df),
    template="plotly_white",
)
fig_net_worth_liq.update_layout(
    xaxis=dict(tickmode="linear"),
    xaxis_title="Month",
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=(dict(showgrid=False)),
)

# Calling the xldate_as_datetime() function to
# convert the specified excel serial date into
# datetime.datetime object


# ---- SIDEBAR ----
# ---- SIDEBAR ----

# ---- MAINPAGE ----
st.title(":bar_chart: Patrimônio")
st.markdown("##")

left_column, middle1_column, middle2_column,right_column,right2_column = st.columns(5)
with left_column:
    st.subheader("Patrimonio Liq. s/caixinha")
    # st.write("Left Subheader")
    st.metric("", networth_str_liq, "R${:,.2f}".format(networth_change))
with middle1_column:
    st.subheader("Saldo Nubank")
    st.write("##")
    st.metric("", "R${:,.2f}".format(data_conta[-1:]["Saldo Líquido"].values[0]))
with middle2_column:
    st.subheader("Caixinha") 
    st.write("##")
    st.metric("", "R${:,.2f}".format(df_caixinha[-1:]["Valor"].values[0]))
with right_column:
    st.subheader("Renda Variável Líq.")
    st.write("##")
    st.metric("", "R${:,.2f}".format(df_datas_carteira_mensal[-1:]["Valor liq"].values[0]))
with right2_column:
    st.subheader("Impostos Stocks")
    st.write("##")
    st.metric("", "R${:,.2f}".format(df_datas_carteira_mensal[-1:]["Imposto"].values[0]))

st.markdown("""---""")

# st.subheader("Net Worth Sem Caixinha")
# st.plotly_chart(fig_net_worth, use_container_width=True)

monthly_tab1, monthly_tab2 = st.tabs(
    ["Net Worth Sem Caixinha", "Net Worth Sem Caixinha Liquida"]
)

with monthly_tab1:
    st.subheader("Net Worth Sem Caixinha")
    st.plotly_chart(fig_net_worth, use_container_width=True)

with monthly_tab2:
    st.subheader("Net Worth Sem Caixinha Liquida")
    st.plotly_chart(fig_net_worth_liq, use_container_width=True)

# ---- MAINPAGE ----

# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
# ---- HIDE STREAMLIT STYLE ----

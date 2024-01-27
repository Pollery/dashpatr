import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
import numpy as np
import warnings

# Suppress FutureWarning
warnings.filterwarnings("ignore", category=FutureWarning)

# Set Streamlit page configuration
st.set_page_config(
    page_title="Gastos (Fatura + Extrato)",
    page_icon=":dollar:",
    layout="wide"
)

# Load custom CSS styles
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Get current date information
current_date = datetime.date.today()
curr_year = current_date.year
curr_month = current_date.month

# Attempt to read spend data from parquet file
try:
    spend_data = pd.read_parquet("./data/Final/spend_data.gzip")
except FileNotFoundError:
    # Handle the case where the first file path is not found
    spend_data = pd.read_parquet("../data/Final/spend_data.gzip")

# Mapping of month numbers to Portuguese month names
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

# Calculate one year ago date
one_year_ago = np.datetime64(datetime.date(curr_year - 1, curr_month, 1))

# Filter data for the past year
filtered_data = spend_data[spend_data["Date"] >= one_year_ago]

# Calculate median amount for the past year
median_amount_past_year = (
    filtered_data.groupby(["Month", "Year"])["Amount"].sum().median()
)

# Calculate monthly budget and YTD budget
monthly_budget = median_amount_past_year
ytd_budget = monthly_budget * curr_month

# Extract current year spend data
ytd_spend = spend_data.loc[spend_data["Year"] == curr_year]
mtd_spend = ytd_spend.loc[ytd_spend["Month"] == curr_month]

# Format MTD spend table for display
mtd_spend_table = mtd_spend.copy()
mtd_spend_table.loc[:, "Amount"] = mtd_spend_table["Amount"].map("${:,.2f}".format)

# Calculate MTD spend total, variance, YTD spend total, YTD variance, monthly average spend, and monthly average spend variance
mtd_spend_total = ytd_spend.loc[ytd_spend["Month"] == curr_month]["Amount"].sum()
mtd_spend_variance = (mtd_spend_total - monthly_budget) * (-1)
total_ytd_spend = ytd_spend["Amount"].sum()
ytd_variance = (total_ytd_spend - ytd_budget) * (-1)
ytd_monthly_average_spend = total_ytd_spend / curr_month
ytd_monthly_average_spend_variance = (ytd_monthly_average_spend - monthly_budget) * (-1)

# Sidebar section
st.sidebar.subheader("Histórico de gastos:")
year = st.sidebar.multiselect(
    "Ano:", options=spend_data["Year"].unique(), default=spend_data["Year"].unique()
)
month = st.sidebar.multiselect(
    "Mês:",
    options=spend_data["Month"].sort_values().map(month_mapping).unique(),
    default=spend_data["Month"].sort_values().map(month_mapping).unique(),
)
account = st.sidebar.multiselect(
    "Banco:",
    options=spend_data["Account"].unique(),
    default=spend_data["Account"].unique(),
)

# Display historical spend data based on user selection
df_selection = spend_data.query("Year == @year & Pretty_Month ==@month & Account == @account")
historical_spend_table = df_selection.copy()
historical_spend_table.loc[:, "Amount"] = historical_spend_table["Amount"].map("${:,.2f}".format)

# Main page section
st.title(":dollar: Gastos (Fatura + Extrato)")
st.markdown("##")

# Metrics section
left_column, middle_column, right_column = st.columns(3)
with left_column:
    st.subheader("Gastos YTD")
    st.metric("", "R${:,.2f}".format(total_ytd_spend), "R${:,.2f}".format(-ytd_variance))
with middle_column:
    st.subheader("Gastos MTD")
    st.metric("", "R${:,.2f}".format(mtd_spend_total), "R${:,.2f}".format(-mtd_spend_variance))
with right_column:
    st.subheader("Média Mensal")
    st.metric("", "R${:,.2f}".format(ytd_monthly_average_spend), "R${:,.2f}".format(-ytd_monthly_average_spend_variance))

st.markdown("##")

# Current month spending section
monthly_tab1, monthly_tab2, monthly_tab3 = st.tabs(
    ["Gastos Do Mês Atual", "Gasto Detalhado Do Mês Atual", "Gastos Do Mês Atual Banco"]
)

with monthly_tab1:
    st.subheader("Gastos Do Mês Atual")
    # Current month spend by category (Treemap chart)
    fig_mtd_spend_by_category = px.treemap(mtd_spend, path=["Category"], values="Amount", title="")
    fig_mtd_spend_by_category.data[0].textinfo = "label+text+value+percent root"
    fig_mtd_spend_by_category.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_mtd_spend_by_category, use_container_width=True)

with monthly_tab2:
    st.subheader("Gasto Detalhado Do Mês Atual")
    # MTD spend table
    fig_monthly_spend_table = go.Figure(
        data=go.Table(
            header=dict(
                values=list(mtd_spend_table[["Date", "Account", "Category", "Amount"]].columns),
                font=dict(color="white", size=16),
                line_color="#222222",
                fill_color="#0083B8",
                align="left",
            ),
            cells=dict(
                values=[
                    mtd_spend_table.Date,
                    mtd_spend_table.Account,
                    mtd_spend_table.Category,
                    mtd_spend_table.Amount,
                ],
                font=dict(color="#eeeeee", size=14),
                height=30,
                line_color="#222222",
                fill_color="#444444",
                align="left",
            ),
        )
    )
    fig_monthly_spend_table.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_monthly_spend_table, use_container_width=True)

with monthly_tab3:
    st.subheader("Gastos Do Mês Atual Banco")
    # Current month spend by account (Treemap chart)
    fig_mtd_spend_by_account = px.treemap(mtd_spend, path=["Account"], values="Amount", title="")
    fig_mtd_spend_by_account.data[0].textinfo = "label+text+value+percent root"
    fig_mtd_spend_by_account.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_mtd_spend_by_account, use_container_width=True)

# Current year spending section
yearly_tab1, yearly_tab2, yearly_tab3 = st.tabs(
    ["Gasto Mensal YTD", "Gasto Por Categoria YTD", "Gasto Por Banco YTD"]
)

with yearly_tab1:
    st.subheader("Gasto Mensal YTD")
    # Spend by month (Bar chart)
    spend_by_month = pd.DataFrame(ytd_spend.groupby(by=["Month"])["Amount"].sum())
    fig_monthly_spend = px.bar(
        spend_by_month,
        x=spend_by_month.index,
        y="Amount",
        title="",
        color_discrete_sequence=["#0083B8"] * len(spend_by_month),
        template="plotly_white",
    )
    fig_monthly_spend.update_layout(
        xaxis=dict(tickmode="linear"),
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=(dict(showgrid=False)),
    )
    fig_monthly_spend.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_monthly_spend, use_container_width=True)

with yearly_tab2:
    st.subheader("Gasto Por Categoria YTD")
    # Spend by category (Treemap chart)
    fig_spend_by_category = px.treemap(ytd_spend, path=["Category"], values="Amount", title="")
    fig_spend_by_category.data[0].textinfo = "label+text+value+percent root"
    fig_spend_by_category.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_spend_by_category, use_container_width=True)

with yearly_tab3:
    st.subheader("Gasto Por Banco YTD")
    # Spend by account (Treemap chart)
    fig_spend_by_account = px.treemap(ytd_spend, path=["Account"], values="Amount", title="")
    fig_spend_by_account.data[0].textinfo = "label+text+value+percent root"
    fig_spend_by_account.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_spend_by_account, use_container_width=True)

# Historical spend section
historical_tab1, historical_tab2, historical_tab3 , historical_tab4 = st.tabs(
    ["Gasto Por Ano","Gasto Por mës", "Gasto Histórico Detalhado", "Gasto Por Ano Por Banco"]
)

with historical_tab1:
    st.subheader("Gasto Por Ano")
    # Spend by year (Bar chart)
    spend_by_year = pd.DataFrame(df_selection.groupby(by=["Year"])["Amount"].sum())
    fig_yearly_spend = px.bar(
        spend_by_year,
        x=spend_by_year.index,
        y="Amount",
        title="",
        color_discrete_sequence=["#0083B8"] * len(spend_by_year),
        template="plotly_white",
    )
    fig_yearly_spend.update_layout(
        xaxis=dict(tickmode="linear"),
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=(dict(showgrid=False)),
    )
    fig_yearly_spend.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_yearly_spend, use_container_width=True)

with historical_tab2:
    st.subheader("Gasto Por Mês")
    # Spend by year (Bar chart)
    spend_by_month = pd.DataFrame(df_selection.groupby(by=["Year","Month"])["Amount"].sum()).reset_index()
    spend_by_month["Month"] = spend_by_month["Month"].map(month_mapping)
    spend_by_month["Month - Year"] = spend_by_month["Month"].astype(str) + " " + spend_by_month["Year"].astype(str)

    fig_yearly_spend = px.bar(
        spend_by_month,
        x=spend_by_month["Month - Year"],
        y="Amount",
        title="",
        color_discrete_sequence=["#0083B8"] * len(spend_by_month),
        template="plotly_white",
    )
    fig_yearly_spend.update_layout(
        xaxis=dict(tickmode="linear"),
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=(dict(showgrid=False)),
    )
    fig_yearly_spend.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_yearly_spend, use_container_width=True)

with historical_tab3:
    st.subheader("Histórico detalhado")
    # Historical spend table
    fig_historical_spend_table = go.Figure(
        data=go.Table(
            header=dict(
                values=list(
                    historical_spend_table[["Date", "Account", "Category", "Amount"]].columns
                ),
                font=dict(color="white", size=16),
                line_color="#222222",
                fill_color="#0083B8",
                align="left",
            ),
            cells=dict(
                values=[
                    historical_spend_table.Date,
                    historical_spend_table.Account,
                    historical_spend_table.Category,
                    historical_spend_table.Amount,
                ],
                font=dict(color="#eeeeee", size=14),
                height=30,
                line_color="#222222",
                fill_color="#444444",
                align="left",
            ),
        )
    )
    fig_historical_spend_table.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_historical_spend_table, use_container_width=True)

with historical_tab4:
    st.subheader("Gasto Por Ano Por Banco")
    # Spend by year and account (Bar chart)
    spend_by_year_account = (
        pd.DataFrame(df_selection.groupby(by=["Year", "Account"])["Amount"].sum())
        .reset_index()
        .set_index("Year")
    )
    fig_yearly_spend_account = px.bar(
        spend_by_year_account,
        x=spend_by_year_account.index,
        y="Amount",
        color="Account",
        title="",
        template="plotly_white",
    )
    fig_yearly_spend_account.update_layout(
        xaxis=dict(tickmode="linear"),
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=(dict(showgrid=False)),
    )
    fig_yearly_spend_account.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_yearly_spend_account, use_container_width=True)




# Hide Streamlit style
hide_st_style = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

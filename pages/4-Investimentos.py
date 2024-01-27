import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

# Load salary data
try:
    df_salario = pd.read_parquet("../data/Final/df_salario.gzip")
except FileNotFoundError:
    df_salario = pd.read_parquet("./data/Final/df_salario.gzip")
salario = df_salario["valor"]

# Configure Streamlit page
st.set_page_config(
    page_title="Renda Variável", page_icon=":chart_with_upwards_trend:", layout="wide"
)

# Apply custom CSS styles
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Set up date variables
currentDate = datetime.date.today()
curr_year = currentDate.year
curr_month = currentDate.month

# Load investment data for monthly and yearly analysis
try:
    df_datas_carteira_mensal_aberto = pd.read_parquet(
        "../data/Final/df_datas_carteira_mensal_aberto.gzip"
    )
except FileNotFoundError:
    df_datas_carteira_mensal_aberto = pd.read_parquet(
        "./data/Final/df_datas_carteira_mensal_aberto.gzip"
    )

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

try:
    df_datas_carteira_mensal = pd.read_parquet(
        "../data/Final/df_datas_carteira_mensal.gzip"
    )
except FileNotFoundError:
    df_datas_carteira_mensal = pd.read_parquet(
        "./data/Final/df_datas_carteira_mensal.gzip"
    )

# Process yearly investment data
df_datas_carteira_mensal["year"] = df_datas_carteira_mensal["Date"].dt.year

df_datas_carteira_anual = df_datas_carteira_mensal.groupby("year").agg(
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
df_datas_carteira_anual["aporte_diff"] = df_datas_carteira_anual["aporte"].diff()
df_datas_carteira_anual["actual_value_brl_diff"] = df_datas_carteira_anual[
    "actual_value_brl"
].diff()
df_datas_carteira_anual["Valor_liq_diff"] = df_datas_carteira_anual["Valor_liq"].diff()

# Process yearly investment data for open assets
df_datas_carteira_mensal_aberto["year"] = df_datas_carteira_mensal_aberto[
    "Date"
].dt.year
df_datas_carteira_mensal_aberto["Lucro_Loss"] = (
    df_datas_carteira_mensal_aberto["actual_value_brl"]
    - df_datas_carteira_mensal_aberto["total"]
)
df_datas_carteira_mensal_aberto["Lucro_Dividendos"] = (
    (
        df_datas_carteira_mensal_aberto["Lucro_Loss"]
        + df_datas_carteira_mensal_aberto["dividends_total"]
    )
    / df_datas_carteira_mensal_aberto["total"]
    * 100
)

df_datas_carteira_anual_aberto = df_datas_carteira_mensal_aberto.groupby(
    ["year", "tipo", "industry", "stock"]
).agg(
    aporte=pd.NamedAgg(column="total", aggfunc="last"),
    actual_value_brl=pd.NamedAgg(column="actual_value_brl", aggfunc="last"),
    Lucro=pd.NamedAgg(column="Lucro", aggfunc="last"),
    Imposto=pd.NamedAgg(column="Imposto", aggfunc="last"),
    dividends_total=pd.NamedAgg(column="dividends_total", aggfunc="last"),
    Valor_liq=pd.NamedAgg(column="Valor liq", aggfunc="last"),
    ipca =pd.NamedAgg(column="ipca", aggfunc="prod"),
    igp_m =pd.NamedAgg(column="igp-m", aggfunc="prod"),
    USD =pd.NamedAgg(column="USD", aggfunc="prod"),
    selic =pd.NamedAgg(column="selic", aggfunc="prod"),
)
df_datas_carteira_anual_aberto = df_datas_carteira_anual_aberto.reset_index()

# Calculate percentage of actual_value_brl for the current year
df_datas_carteira_anual_aberto_2024 = df_datas_carteira_anual_aberto.loc[
    df_datas_carteira_anual_aberto["year"] == curr_year
]
df_datas_carteira_anual_aberto_2024["pct_actual_value_brl"] = round(
    (
        df_datas_carteira_anual_aberto_2024["actual_value_brl"]
        / df_datas_carteira_anual_aberto_2024["actual_value_brl"].sum()
        * 100
    ),
    2,
)
df_datas_carteira_anual_aberto_2024["actual_value_brl"] = round(
    df_datas_carteira_anual_aberto_2024["actual_value_brl"], 2
)

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


# Calculate key metrics
total_investments = df_datas_carteira_anual[-1:]["actual_value_brl"].values[0]
ytd_earnings = salario * currentDate.month
ytd_contributions = df_datas_carteira_anual[-1:]["aporte_diff"].values[0]
ytd_portfolio_performance = (
    df_datas_carteira_anual[-1:]["Lucro"].values[0]
    / df_datas_carteira_anual[-1:]["aporte"].values[0]
)
ytd_dividends = df_datas_carteira_anual[-1:]["dividends_total"].values[0]

# Sidebar
st.title(":chart_with_upwards_trend: Investimentos em Renda Variável")
st.markdown("##")

# Display key metrics in columns
column_1, column_2, column_3, column_4, column_5, column_6 = st.columns(6)
with column_1:
    st.subheader("Valor Atual")
    st.metric("", "R${:,.2f}".format(total_investments))
with column_2:
    st.subheader("Lucro/Perda")
    st.metric("", "R${:,.2f}".format(float(ytd_earnings)))
with column_3:
    st.subheader("Performance YTD")
    st.metric("", "{}%".format(round(ytd_portfolio_performance * 100, 2)))
with column_4:
    st.subheader("Aportes YTD")
    st.metric("", "R${:,.2f}".format(ytd_contributions))
with column_5:
    st.subheader("Salário YTD")
    st.metric("", "R${:,.2f}".format(float(ytd_earnings)))
with column_6:
    st.subheader("Dividendos")
    st.metric("", "R${:,.2f}".format(ytd_dividends))

st.markdown("##")

# Asset Allocation and Sector Allocation Tabs
allocation_tab1, allocation_tab2, allocation_tab3 = st.tabs(
    ["Tipo de Investimento", "Ativos", "Setores"]
)

# Display asset allocation in treemap chart for each tab
with allocation_tab1:
    st.subheader("Tipo de Investimento")
    fig = px.treemap(
        df_datas_carteira_anual_aberto_2024,
        path=["tipo"],
        values="actual_value_brl",
        title="",
    )
    fig.data[0].textinfo = "label+text+value+percent root"
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig, use_container_width=True)

with allocation_tab2:
    st.subheader("Ativos")
    fig = px.treemap(
        df_datas_carteira_anual_aberto_2024,
        path=["stock"],
        values="actual_value_brl",
        title="",
    )
    fig.data[0].textinfo = "label+text+value+percent root"
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig, use_container_width=True)

with allocation_tab3:
    st.subheader("Setores")
    fig = px.treemap(
        df_datas_carteira_anual_aberto_2024,
        path=["industry"],
        values="actual_value_brl",
        title="",
    )
    fig.data[0].textinfo = "label+text+value+percent root"
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig, use_container_width=True)

# Annual Evolution Tabs
historical_tab1, historical_tab2, historical_tab3 = st.tabs(
    ["Tipo de investimento", "Ativos", "Setores"]
)

# Display annual evolution in bar chart for each tab
with historical_tab1:
    st.subheader("Tipo de investimento")
    spend_by_year = pd.DataFrame(
        df_datas_carteira_anual_aberto.groupby(by=["year", "tipo"])[
            "pct_actual_value_brl"
        ]
        .sum()
        .reset_index()
    )
    spend_by_year["pct_actual_value_brl"] = round(
        spend_by_year["pct_actual_value_brl"], 2
    )
    fig = px.bar(
        spend_by_year,
        x=spend_by_year["year"],
        y="pct_actual_value_brl",
        title="",
        color="tipo",
        text_auto=True,
        template="plotly_white",
    )
    fig.update_layout(
        xaxis=dict(tickmode="linear"),
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=(dict(showgrid=False)),
    )
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    fig.update_traces(
        text=[f"{val}\u00A3" for val in spend_by_year["pct_actual_value_brl"]]
    )
    st.plotly_chart(fig, use_container_width=True)

with historical_tab2:
    st.subheader("Ativos")
    spend_by_year = pd.DataFrame(
        df_datas_carteira_anual_aberto.groupby(by=["year", "stock"])[
            "pct_actual_value_brl"
        ]
        .sum()
        .reset_index()
    )
    spend_by_year["pct_actual_value_brl"] = round(
        spend_by_year["pct_actual_value_brl"], 2
    )
    fig = px.bar(
        spend_by_year,
        x=spend_by_year["year"],
        y="pct_actual_value_brl",
        title="",
        color="stock",
        text_auto=True,
        template="plotly_white",
    )
    fig.update_layout(
        xaxis=dict(tickmode="linear"),
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=(dict(showgrid=False)),
    )
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    fig.update_traces(text=[f"{val}%" for val in spend_by_year["pct_actual_value_brl"]])
    st.plotly_chart(fig, use_container_width=True)

with historical_tab3:
    st.subheader("Setores")
    spend_by_year = pd.DataFrame(
        df_datas_carteira_anual_aberto.groupby(by=["year", "industry"])[
            "pct_actual_value_brl"
        ]
        .sum()
        .reset_index()
    )
    spend_by_year["pct_actual_value_brl"] = round(
        spend_by_year["pct_actual_value_brl"], 2
    )
    fig = px.bar(
        spend_by_year,
        x=spend_by_year["year"],
        y="pct_actual_value_brl",
        title="",
        color="industry",
        text_auto=True,
        template="plotly_white",
    )
    fig.update_layout(
        xaxis=dict(tickmode="linear"),
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=(dict(showgrid=False)),
    )
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    fig.update_traces(text=[f"{val}%" for val in spend_by_year["pct_actual_value_brl"]])
    st.plotly_chart(fig, use_container_width=True)

# crescimento

# Annual Evolution Tabs
tab1, tab2, tab3 = st.tabs(["Crescimento", "Crescimento Ativos", "Setores"])

# Display annual evolution in bar chart for each tab'
with tab1:
    st.subheader("Crescimento Ativos Hoje")
    fig = px.bar(
        df_datas_carteira_anual_aberto.loc[
            df_datas_carteira_anual_aberto["year"] == curr_year
        ].groupby("year")["Lucro_Dividendos"].sum().reset_index(),
        x="year",
        y="Lucro_Dividendos",
    )
    fig["layout"]["yaxis"]["title"] = "Lucro + Dividendos %"
    fig["layout"]["xaxis"]["title"] = "Ano"

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        template="plotly_white",
    )

    fig.update_traces(
        text=[
            f"{round(val,2)}%"
            for val in df_datas_carteira_anual_aberto.loc[
                df_datas_carteira_anual_aberto["year"] == curr_year
            ]["Lucro_Dividendos"]
        ]
    )
    st.plotly_chart(fig, use_container_width=True)



# with tab10:
# df_tab1 = pd.DataFrame(
#     df_datas_carteira_anual_aberto.groupby("year")["Lucro_Dividendos"]
#     .sum()
#     .reset_index()
# )
# df_tab1["year"] = pd.Categorical(df_tab1["year"])
# valores_y = tuple(df_tab1["Lucro_Dividendos"])
#  IMPOSSIVEL
#     st.subheader("Setores")
#     # Plot the bar chart
#     fig10 = px.bar(
#         df_tab1,
#         x=valores_y,
#         y="Lucro_Dividendos",
#         title="Annual Evolution of Lucro_Dividendos",
#         text=df_tab1["Lucro_Dividendos"].apply(lambda x: f"{x:.2f}%"),  # Format as percentage
#         template="plotly_white",
#     )
    
#     # Customize the layout
#     fig10.update_xaxes(type="category")
#     fig10.update_layout(
#         xaxis=dict(tickmode="linear"),
#         plot_bgcolor="rgba(0,0,0,0)",
#         yaxis=dict(showgrid=False),
#         margin=dict(l=0, r=0, t=0, b=0),
#     )
    
#     # Show the chart in Streamlit app
#     st.plotly_chart(fig10, use_container_width=True)
with tab2:
    st.subheader("Crescimento Ativos Hoje")
    fig = px.bar(
        df_datas_carteira_anual_aberto.loc[
            df_datas_carteira_anual_aberto["year"] == curr_year
        ],
        x="stock",
        y="Lucro_Dividendos",
    )
    fig["layout"]["yaxis"]["title"] = "Lucro + Dividendos %"
    fig["layout"]["xaxis"]["title"] = "stock"

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        template="plotly_white",
    )

    fig.update_traces(
        text=[
            f"{round(val,2)}%"
            for val in df_datas_carteira_anual_aberto.loc[
                df_datas_carteira_anual_aberto["year"] == curr_year
            ]["Lucro_Dividendos"]
        ]
    )
    st.plotly_chart(fig, use_container_width=True)
    # fig.update(layout_yaxis_range = [-100,100])

with tab3:
    st.subheader("Crescimento Setores Hoje")
    fig = px.bar(
        df_datas_carteira_anual_aberto.loc[
            df_datas_carteira_anual_aberto["year"] == curr_year
        ],
        x="industry",
        y="Lucro_Dividendos",
    )
    fig["layout"]["yaxis"]["title"] = "Lucro + Dividendos %"
    fig["layout"]["xaxis"]["title"] = "Industry"
    fig.update_layout(
        title="",
        width=600,
        height=400,
        template="plotly_white",
    )
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    fig.update_traces(
        text=[
            f"{round(val,2)}%"
            for val in df_datas_carteira_anual_aberto.loc[
                df_datas_carteira_anual_aberto["year"] == curr_year
            ]["Lucro_Dividendos"]
        ]
    )
    st.plotly_chart(fig, use_container_width=True)



st.markdown("##")
st.markdown("##")

# Hide Streamlit style
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

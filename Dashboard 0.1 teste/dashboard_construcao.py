import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Dashboard Construção Civil", layout="wide")

st.title("🏗️ Dashboard de Projetos de Construção Civil")

# --- CARREGAR DADOS ---
@st.cache_data
def carregar_dados():
    df = pd.read_csv("construcao_civil_sem_acentos.csv")
    return df

df = carregar_dados()

# --- FILTROS LATERAIS ---
st.sidebar.header("Filtros 🔍")

regioes = st.sidebar.multiselect(
    "Selecione a região:",
    options=df["regiao"].unique(),
    default=df["regiao"].unique()
)

projetos = st.sidebar.multiselect(
    "Selecione o tipo de projeto:",
    options=df["projeto"].unique(),
    default=df["projeto"].unique()
)

# --- FILTRAR DADOS ---
df_filtrado = df.query("regiao in @regioes and projeto in @projetos")

# --- MÉTRICAS PRINCIPAIS ---
st.subheader("📊 Visão Geral dos Projetos")

col1, col2, col3 = st.columns(3)
col1.metric("Total de Projetos", len(df_filtrado))
col2.metric("Custo Médio (R$)", f"{df_filtrado['custo'].mean():,.2f}")
col3.metric("Custo Total (R$)", f"{df_filtrado['custo'].sum():,.2f}")

# --- GRÁFICO DE BARRAS ---
st.subheader("💰 Custo Médio por Tipo de Construção")
grafico_barra = px.bar(
    df_filtrado.groupby("projeto")["custo"].mean().reset_index(),
    x="projeto",
    y="custo",
    title="Custo médio por tipo de projeto",
    text_auto=".2s",
    color="projeto"
)
st.plotly_chart(grafico_barra, use_container_width=True)

# --- GRÁFICO DE PIZZA ---
st.subheader("📍 Distribuição de Projetos por Região")
grafico_pizza = px.pie(
    df_filtrado,
    names="regiao",
    title="Distribuição de projetos por região",
    hole=0.4
)
st.plotly_chart(grafico_pizza, use_container_width=True)

# --- TABELA DE DADOS ---
st.subheader("📋 Detalhes dos Projetos")
st.dataframe(df_filtrado, use_container_width=True)
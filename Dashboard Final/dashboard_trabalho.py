# Dashboard feito em Streamlit com gráficos Plotly e WordCloud
# Mostra métricas, tendências e proporções de custos, funcionários e projetos

# ---- Importação das bibliotecas principais ----
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# Cria um tema escuro personalizado chamado "construcao_dark"
pio.templates["construcao_dark"] = pio.templates["plotly_dark"]
pio.templates["construcao_dark"].layout.update(
    font=dict(family="Segoe UI,sans-serif",
              size=14,
              color="#F3F5F7"),
    title=dict(x=0.5,
               font=dict(size=22, color="#00E0FF")), # centraliza o título
    paper_bgcolor="#0B1F3A", # fundo da área total
    plot_bgcolor="#0B1F3A",) # fundo da área de plotagem
pio.templates.default = "construcao_dark" # define esse tema como padrão


# Define algumas características da aba no navegador, como título e título
st.set_page_config(
    page_title="🏗️ Dashboard Construção Civil",
    page_icon="🏙️",
    layout="wide")

# Adiciona estilos HTML e CSS para personalizar a aparência da interface
st.markdown("""
<style>
.stApp {background-color: #0B1F3A; color: #F3F5F7; font-family: 'Segoe UI', sans-serif;}
h1 {color: #00E0FF; text-align: center; margin-bottom: 0.3em; font-weight: 700;}
.metric-card {background: #123057; padding: 20px; border-radius: 18px; box-shadow: 0 6px 18px rgba(0,0,0,0.5); text-align: center; transition: transform 0.3s, box-shadow 0.3s;}
.metric-card:hover {transform: translateY(-6px); box-shadow: 0 12px 25px rgba(0,0,0,0.7);}
.metric-icon {font-size: 40px; margin-bottom: 10px;}
.metric-value {font-size: 28px; font-weight: 700; color: #00E0FF;}
.metric-label {font-size: 16px; color: #F3F5F7;}
.metric-change {font-size:14px; font-weight:600; margin-top:4px;}
.metric-up {color:#00FF7F;}
.metric-down {color:#FF4500;}
.stSidebar .css-1d391kg {background-color: #123057; padding: 15px; border-radius: 15px;}
.stSidebar h2, .stSidebar h3, .stSidebar label {color: #F3F5F7;}
</style>
""", unsafe_allow_html=True)

# Define o título da Dashboard
st.title("🏗️ Dashboard Construção Civil")

@st.cache_data(ttl=3600)
def carregar_dados():
    # carrega o .csv que tem nome padronizado, especificando as colunas
    df = pd.read_csv("relatorio_construcoes.csv",
                     usecols=[
                         "Data",
                         "Nome",
                         "Sexo",
                         "Regiao",
                         "Projeto",
                         "Funcionarios",
                         "Tempo_conclusao_dias",
                         "Custo_Reais"])
    # converte a coluna Data para um formato datetime do pandas
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
    # remove linhas sem data válida
    df.dropna(subset=["Data"], inplace=True)
    return df

df = carregar_dados()

# Cria o menu vertical que controla os filtos
st.sidebar.header("🎛️ Filtros Avançados")

# Cria o filtro de regiões
regioes = st.sidebar.multiselect("🌍 Região:",
                                 sorted(df["Regiao"].unique()),
                                 default=df["Regiao"].unique())

# Cria o filtro de tipos de projeto
projetos = st.sidebar.multiselect("🏗️ Tipo de Projeto:",
                                  sorted(df["Projeto"].unique()),
                                  default=df["Projeto"].unique())

# Cria o filtro com base no ano dos projetos
anos = st.sidebar.multiselect("🗓️ Anos dos Projetos:",
                              sorted(df["Data"].dt.year.unique()),
                              default=df["Data"].dt.year.unique())

# Filtra o df checando cada condição e retorna um df já filtrado
df_filtrado = df[df["Regiao"].isin(regioes) & df["Projeto"].isin(projetos) & df["Data"].dt.year.isin(anos)]

# Cria gráficos de linha simplificados usados nos cards de métricas
def criar_sparkline(df, coluna_valor, coluna_data, cor="#00E0FF"):
    df_spark = df.groupby(coluna_data,
                          observed=True,
                          sort=True)[coluna_valor].sum().reset_index()

    # Cria um gráfico de linha simples (sparkline) mostrando tendência
    fig = go.Figure(go.Scatter(x=df_spark[coluna_data],
                               y=df_spark[coluna_valor],
                               mode='lines',
                               line=dict(color=cor, width=2),
                               fill='tozeroy'))

    # Remove eixos e margens para um visual limpo
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0),
                      xaxis=dict(showgrid=False, visible=False),
                      yaxis=dict(showgrid=False, visible=False),
                      paper_bgcolor='#123057', plot_bgcolor='#123057')

    return fig

# Aplica o layout escuro e mantém o padrão visual da dashboard
def aplicar_dark_layout(fig):
    fig.update_layout(paper_bgcolor="#0B1F3A",
                      plot_bgcolor="#0B1F3A",
                      font_color="#F3F5F7",
                      title_font_color="#00E0FF",
                      legend=dict(font=dict(color="#F3F5F7")),
                      xaxis=dict(color="#F3F5F7", gridcolor="#1A3B60"),
                      yaxis=dict(color="#F3F5F7", gridcolor="#1A3B60"))
    return fig

# Calcula o percentual de crescimento entre os dois períodos mais recentes
def calcular_crescimento(df, coluna):
    df_sorted = df.sort_values("Data")
    # Se houver menos de duas datas, retorna 0 para evitar erro
    if df_sorted["Data"].nunique() < 2:
        return 0
    ultimo = df_sorted[df_sorted["Data"] == df_sorted["Data"].max()][coluna].sum()
    anterior = df_sorted[df_sorted["Data"] == df_sorted["Data"].unique()[-2]][coluna].sum()
    return 0 if anterior == 0 else (ultimo - anterior) / anterior * 100

# Calcula alguns valores já usando o df que passou pelos filtros avançados
total_custo = df_filtrado["Custo_Reais"].sum()
custo_medio = df_filtrado["Custo_Reais"].mean()
media_funcionarios = df_filtrado["Funcionarios"].mean()
media_tempo = df_filtrado["Tempo_conclusao_dias"].mean()
crescimento_custo = calcular_crescimento(df_filtrado, "Custo_Reais")
crescimento_func = calcular_crescimento(df_filtrado, "Funcionarios")
crescimento_tempo = calcular_crescimento(df_filtrado, "Tempo_conclusao_dias")

# Converte o separador de milhar da vírgula (,) para o ponto (.)
total_custo_formatado = f'{total_custo:,.0f}'.replace(',', '.')
custo_medio_formatado = f'{custo_medio:,.0f}'.replace(',', '.')

# Cria uma exibição com 4 colunas para os cards de métricas
col1, col2, col3, col4 = st.columns(4)

# Cada bloco a seguir cria um card de métrica com sparkline abaixo

with col1:
    # Card de custo total
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-icon'>💰</div>
        <div class='metric-value'>R$ {total_custo_formatado}</div>
        <div class='metric-label'>Custo Total</div>
        <div class='metric-change {"metric-up" if crescimento_custo>=0 else "metric-down"}'>
            {"▲" if crescimento_custo>=0 else "▼"} {abs(crescimento_custo):.1f}%
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.plotly_chart(criar_sparkline(df_filtrado,
                                    "Custo_Reais",
                                    "Data",
                                    "#00E0FF"),
                                    config={"displayModeBar": False,
                                            "width": "content"},
                                    key="spark_custo")

with col2:
    # Card de custo médio
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-icon'>📊</div>
        <div class='metric-value'>R$ {custo_medio_formatado}</div>
        <div class='metric-label'>Custo Médio</div>
        <div class='metric-change {"metric-up" if crescimento_func>=0 else "metric-down"}'>
            {"▲" if crescimento_func>=0 else "▼"} {abs(crescimento_func):.1f}%
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.plotly_chart(criar_sparkline(df_filtrado,
                                    "Custo_Reais",
                                    "Data", "#33CFFF"),
                                    config={"displayModeBar": False,
                                            "width": "content"},
                                    key="spark_medio")

with col3:
    # Card de média de funcionários
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-icon'>👷</div>
        <div class='metric-value'>{media_funcionarios:,.0f}</div>
        <div class='metric-label'>Média de Funcionários</div>
        <div class='metric-change {"metric-up" if crescimento_func>=0 else "metric-down"}'>
            {"▲" if crescimento_func>=0 else "▼"} {abs(crescimento_func):.1f}%
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.plotly_chart(criar_sparkline(df_filtrado,
                                    "Funcionarios",
                                    "Data",
                                    "#88E0FF"),
                                    config={"displayModeBar": False,
                                            "width": "content"},
                                    key="spark_funcionarios")

with col4:
    # Card de tempo médio de conclusão
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-icon'>⏱️</div>
        <div class='metric-value'>{media_tempo:,.0f} dias</div>
        <div class='metric-label'>Duração Média</div>
        <div class='metric-change {"metric-up" if crescimento_tempo>=0 else "metric-down"}'>
            {"▲" if crescimento_tempo>=0 else "▼"} {abs(crescimento_tempo):.1f}%
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.plotly_chart(criar_sparkline(df_filtrado,
                                    "Tempo_conclusao_dias",
                                    "Data",
                                    "#00BFFF"),
                                    config={"displayModeBar": False,
                                            "width": "content"},
                                    key="spark_tempo")

# Cria uma linha de separação na página web da Dashboard
st.markdown("---")

# Inicia a área de gráficos principais em duas colunas
col1, col2 = st.columns(2)
with col1:
    # Gráfico de barras: custo total por tipo de projeto
    fig1 = px.bar(df_filtrado.groupby("Projeto", observed=True)["Custo_Reais"].sum().reset_index(),
                  x="Projeto",
                  y="Custo_Reais",
                  color="Projeto",
                  labels={"Custo_Reais": "Custos"},
                  text_auto=True,
                  color_discrete_sequence=["#33CFFF", "#00E0FF", "#88E0FF", "#00BFFF"],
                  title="💰 Custo Total por Tipo de Projeto")
    aplicar_dark_layout(fig1)
    st.plotly_chart(fig1, config={"width": "content"}, key="fig1")

with col2:
    # Gráfico de barras: custo médio por tipo de projeto
    fig2 = px.bar(df_filtrado.groupby("Projeto", observed=True)["Custo_Reais"].mean().reset_index(),
               x="Projeto",
               y="Custo_Reais",
               color="Projeto",
               labels={"Custo_Reais": "Média de Custos"},
               text_auto=True,
               color_discrete_sequence=["#33CFFF", "#00E0FF", "#88E0FF", "#00BFFF"],
               title="💰 Custo Médio por Tipo de Projeto")
    aplicar_dark_layout(fig2)
    st.plotly_chart(fig2, config={"width": "content"}, key="fig2")

# Cria uma nova linha de dois gráficos
col1, col2 = st.columns(2)

with col1:
    # Boxplot mostrando a variação no número de funcionários por projeto
    fig3 = px.box(df_filtrado,
              x="Projeto",
              y="Funcionarios",
              color="Projeto",
              labels={"Funcionarios": "Funcionários"},
              points="all",
              color_discrete_sequence=["#33CFFF", "#88E0FF", "#00E0FF"],
              title="👷 Distribuição de Funcionários por Tipo de Projeto")
    aplicar_dark_layout(fig3)
    st.plotly_chart(fig3, config={"width": "content"}, key="fig3")

with col2:
    # Gráfico de pizza mostrando a proporção de custos por região
    fig4 = px.pie(df_filtrado,
                  names="Regiao",
                  values="Custo_Reais",
                  hole=0.4,
                  color_discrete_sequence=px.colors.sequential.Reds,
                  labels={"Custo_Reais": "Custos"},
                  title="🌎 Proporção dos Custos por Região")
    aplicar_dark_layout(fig4)
    st.plotly_chart(fig4, config={"width": "content"}, key="fig4")

# Cria um gráfico de linha para acompanhar a evolução dos custos ao longo do tempo
fig5 = px.line(df_filtrado.sort_values("Data"),
               x="Data",
               y="Custo_Reais",
               color="Projeto",
               labels={"Custo_Reais": "Custos"},
               markers=True,
               color_discrete_sequence=["#33FF5F", "#00E0FF", "#FDFF88", "#4400FF"],
               title="📅 Tendência de Custos por Projeto")
aplicar_dark_layout(fig5)
# Aumenta a espessura das linhas para melhor visualização
fig5.update_traces(line=dict(width=3))
st.plotly_chart(fig5, config={"width": "content"}, key="fig5")

# Adiciona uma linha divisória antes da nuvem de palavras
st.markdown("---")

# Cria um título HTML centralizado
st.markdown("<h2 style='text-align:center; color:#00E0FF;'>☁️ Nuvem de Palavras - Projetos</h2>", unsafe_allow_html=True)

# Junta todos os nomes dos projetos em uma única string
textos = " ".join(df_filtrado["Projeto"].astype(str).tolist())

# Gera a nuvem de palavras apenas se houver texto suficiente
if textos.strip():
    wordcloud = WordCloud(width=800,
                          height=300,
                          background_color="#0B1F3A",
                          colormap="Blues",
                          prefer_horizontal=0.9,
                          max_words=80,
                          collocations=False,
                          contour_color="#00E0FF",
                          contour_width=2).generate(textos)
    # Plota a nuvem de palavras
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig, width="content")
else:
    # Caso não haja projetos suficientes para gerar a nuvem
    st.info("Não há dados suficientes para gerar a nuvem de palavras.")

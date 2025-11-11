import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import matplotlib.pyplot as plt
from wordcloud import WordCloud

pio.templates["construcao_dark"] = pio.templates["plotly_dark"]
pio.templates["construcao_dark"].layout.update(
    font=dict(family="Segoe UI, sans-serif", size=14, color="#F3F5F7"),
    title=dict(x=0.5, font=dict(size=22, color="#00E0FF")),
    paper_bgcolor="#0B1F3A",
    plot_bgcolor="#0B1F3A",
)
pio.templates.default = "construcao_dark"

st.set_page_config(
    page_title="🏗️ Dashboard Construção Civil",
    page_icon="🏙️",
    layout="wide"
)

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

st.title("🏗️ Dashboard Construção Civil")

@st.cache_data(ttl=3600)
def carregar_dados():
    df = pd.read_csv("base_construcao_civil.csv", usecols=[
        "Data", "Nome", "Sexo", "Regiao", "Projeto", 
        "Funcionarios", "Tempo_conclusao_dias", "Custo_Reais"
    ])
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
    df.dropna(subset=["Data"], inplace=True)
    return df

df = carregar_dados()

st.sidebar.header("🎛️ Filtros Avançados")
regioes = st.sidebar.multiselect("🌍 Região:", sorted(df["Regiao"].unique()), default=df["Regiao"].unique())
projetos = st.sidebar.multiselect("🏗️ Tipo de Projeto:", sorted(df["Projeto"].unique()), default=df["Projeto"].unique())

df_filtrado = df[df["Regiao"].isin(regioes) & df["Projeto"].isin(projetos)]

def criar_sparkline(df, coluna_valor, coluna_data, cor="#00E0FF"):
    df_spark = df.groupby(coluna_data, observed=True, sort=True)[coluna_valor].sum().reset_index()
    fig = go.Figure(go.Scatter(x=df_spark[coluna_data], y=df_spark[coluna_valor],
                               mode='lines', line=dict(color=cor, width=2), fill='tozeroy'))
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0),
                      xaxis=dict(showgrid=False, visible=False),
                      yaxis=dict(showgrid=False, visible=False),
                      paper_bgcolor='#123057', plot_bgcolor='#123057')
    return fig

def aplicar_dark_layout(fig):
    fig.update_layout(paper_bgcolor="#0B1F3A", plot_bgcolor="#0B1F3A",
                      font_color="#F3F5F7", title_font_color="#00E0FF",
                      legend=dict(font=dict(color="#F3F5F7")),
                      xaxis=dict(color="#F3F5F7", gridcolor="#1A3B60"),
                      yaxis=dict(color="#F3F5F7", gridcolor="#1A3B60"))
    return fig

def calcular_crescimento(df, coluna):
    df_sorted = df.sort_values("Data")
    if df_sorted["Data"].nunique() < 2:
        return 0
    ultimo = df_sorted[df_sorted["Data"] == df_sorted["Data"].max()][coluna].sum()
    anterior = df_sorted[df_sorted["Data"] == df_sorted["Data"].unique()[-2]][coluna].sum()
    return 0 if anterior == 0 else (ultimo - anterior) / anterior * 100

total_custo = df_filtrado["Custo_Reais"].sum()
custo_medio = df_filtrado["Custo_Reais"].mean()
media_funcionarios = df_filtrado["Funcionarios"].mean()
media_tempo = df_filtrado["Tempo_conclusao_dias"].mean()

crescimento_custo = calcular_crescimento(df_filtrado, "Custo_Reais")
crescimento_func = calcular_crescimento(df_filtrado, "Funcionarios")
crescimento_tempo = calcular_crescimento(df_filtrado, "Tempo_conclusao_dias")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-icon'>💰</div>
        <div class='metric-value'>R$ {total_custo:,.0f}</div>
        <div class='metric-label'>Custo Total</div>
        <div class='metric-change {"metric-up" if crescimento_custo>=0 else "metric-down"}'>
            {"▲" if crescimento_custo>=0 else "▼"} {abs(crescimento_custo):.1f}%
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.plotly_chart(criar_sparkline(df_filtrado, "Custo_Reais", "Data", "#00E0FF"), use_container_width=True, config={"displayModeBar": False}, key="spark_custo")

with col2:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-icon'>📊</div>
        <div class='metric-value'>R$ {custo_medio:,.0f}</div>
        <div class='metric-label'>Custo Médio</div>
    </div>
    """, unsafe_allow_html=True)
    st.plotly_chart(criar_sparkline(df_filtrado, "Custo_Reais", "Data", "#33CFFF"), use_container_width=True, config={"displayModeBar": False}, key="spark_medio")

with col3:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-icon'>👷</div>
        <div class='metric-value'>{media_funcionarios:,.0f}</div>
        <div class='metric-label'>Funcionários Médios</div>
        <div class='metric-change {"metric-up" if crescimento_func>=0 else "metric-down"}'>
            {"▲" if crescimento_func>=0 else "▼"} {abs(crescimento_func):.1f}%
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.plotly_chart(criar_sparkline(df_filtrado, "Funcionarios", "Data", "#88E0FF"), use_container_width=True, config={"displayModeBar": False}, key="spark_funcionarios")

with col4:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-icon'>⏱️</div>
        <div class='metric-value'>{media_tempo:,.0f} dias</div>
        <div class='metric-label'>Tempo Médio</div>
        <div class='metric-change {"metric-up" if crescimento_tempo>=0 else "metric-down"}'>
            {"▲" if crescimento_tempo>=0 else "▼"} {abs(crescimento_tempo):.1f}%
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.plotly_chart(criar_sparkline(df_filtrado, "Tempo_conclusao_dias", "Data", "#00BFFF"), use_container_width=True, config={"displayModeBar": False}, key="spark_tempo")

st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    fig1 = px.bar(df_filtrado.groupby("Projeto", observed=True)["Custo_Reais"].sum().reset_index(),
                  x="Projeto", y="Custo_Reais", color="Projeto", text_auto=True,
                  color_discrete_sequence=["#33CFFF", "#00E0FF", "#88E0FF", "#00BFFF"],
                  title="💰 Custo Total por Tipo de Projeto")
    aplicar_dark_layout(fig1)
    st.plotly_chart(fig1, use_container_width=True, key="fig1")

with col2:
    fig2 = px.pie(df_filtrado, names="Regiao", values="Custo_Reais", hole=0.4,
                  color_discrete_sequence=px.colors.sequential.Blues,
                  title="🌎 Proporção dos Custos por Região")
    aplicar_dark_layout(fig2)
    st.plotly_chart(fig2, use_container_width=True, key="fig2")

fig3 = px.line(df_filtrado.sort_values("Data"), x="Data", y="Custo_Reais",
               color="Projeto", markers=True,
               color_discrete_sequence=["#33CFFF", "#00E0FF", "#88E0FF", "#00BFFF"],
               title="📅 Tendência de Custos por Projeto")
aplicar_dark_layout(fig3)
fig3.update_traces(line=dict(width=3))
st.plotly_chart(fig3, use_container_width=True, key="fig3")

fig4 = px.box(df_filtrado, x="Projeto", y="Funcionarios", color="Projeto", points="all",
              color_discrete_sequence=["#33CFFF", "#88E0FF", "#00E0FF"],
              title="👷 Distribuição de Funcionários por Tipo de Projeto")
aplicar_dark_layout(fig4)
st.plotly_chart(fig4, use_container_width=True, key="fig4")

st.markdown("---")
st.markdown("<h2 style='text-align:center; color:#00E0FF;'>☁️ Nuvem de Palavras - Projetos</h2>", unsafe_allow_html=True)

textos = " ".join(df_filtrado["Projeto"].astype(str).tolist())
if textos.strip():
    wordcloud = WordCloud(width=800, height=300, background_color="#0B1F3A",
                          colormap="Blues", prefer_horizontal=0.9, max_words=80,
                          collocations=False, contour_color="#00E0FF", contour_width=2).generate(textos)
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig, use_container_width=True)
else:
    st.info("Não há dados suficientes para gerar a nuvem de palavras.")

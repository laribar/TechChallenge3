import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuração inicial ---
st.set_page_config(page_title="Análise PNAD COVID", layout="wide")
st.title("📊 Análise Exploratória - PNAD COVID")

# --- Upload de dados CSV tratados ---
st.sidebar.header("Upload dos dados")
df_pop = st.sidebar.file_uploader("Populacional", type=["csv"])
df_sint = st.sidebar.file_uploader("Sintomas", type=["csv"])
df_comp = st.sidebar.file_uploader("Comportamento", type=["csv"])
df_eco = st.sidebar.file_uploader("Econômico", type=["csv"])

if df_pop and df_sint and df_comp and df_eco:
    df_populacao = pd.read_csv(df_pop)
    df_sintomas = pd.read_csv(df_sint)
    df_comportamento = pd.read_csv(df_comp)
    df_economia = pd.read_csv(df_eco)

    st.success("✅ Dados carregados com sucesso!")

    # --- Seletor de mês e UF ---
    meses = sorted(df_sintomas['mes'].unique())
    ufs = sorted(df_populacao['UF'].unique())
    mes_sel = st.sidebar.selectbox("Selecione o mês", meses)
    uf_sel = st.sidebar.selectbox("Selecione o estado (UF)", ufs)

    # --- Filtro aplicado ---
    df_filtrado = df_sintomas[df_sintomas['mes'] == mes_sel]
    df_filtrado = df_filtrado[df_filtrado['UF'] == uf_sel]

    st.header(f"🔎 Análise em {uf_sel} - Mês {mes_sel}")

    # --- Frequência de sintomas ---
    st.subheader("🧐 Frequência de Sintomas Reportados")
    col_sintomas = df_filtrado.drop(columns=["UF", "Numero_selecao_domicilio", "mes"])
    col_sintomas = col_sintomas.replace({"Sim": 1, "Não": 0})
    freq = col_sintomas.sum().sort_values(ascending=False).reset_index()
    freq.columns = ["Sintoma", "Total"]
    fig = px.bar(freq, x="Sintoma", y="Total", title="Frequência de Sintomas", labels={"Total": "Número de Pessoas"})
    st.plotly_chart(fig, use_container_width=True)

    # --- Internação por faixa etária ---
    st.subheader("🏥 Internações por Faixa Etária")
    df_merge = df_populacao.merge(df_sintomas, on=["UF", "Numero_selecao_domicilio"])
    df_merge = df_merge[df_merge['UF'] == uf_sel]
    df_merge['Faixa_Idade'] = pd.cut(df_merge['Idade'], bins=[0, 17, 30, 45, 60, 80, 120],
                                     labels=['0-17', '18-30', '31-45', '46-60', '61-80', '80+'])
    internacoes = df_merge[df_merge['Internacao_hospitalar'] == 'Sim']
    graf = internacoes['Faixa_Idade'].value_counts().sort_index().reset_index()
    graf.columns = ["Faixa Etária", "Internações"]
    fig2 = px.bar(graf, x="Faixa Etária", y="Internações", title="Internações por Faixa Etária")
    st.plotly_chart(fig2, use_container_width=True)

    # --- Rendimento médio por febre ---
    st.subheader("📈 Rendimento Médio por Febre")
    df_rend = df_sintomas.merge(df_economia, on=["UF", "Numero_selecao_domicilio", "mes"])
    df_rend = df_rend[df_rend['UF'] == uf_sel]
    df_rend['Faixa_rendimento'] = pd.to_numeric(df_rend['Faixa_rendimento'], errors='coerce')
    media = df_rend.groupby("Febre")["Faixa_rendimento"].mean().reset_index()
    fig3 = px.bar(media, x="Febre", y="Faixa_rendimento", title="Rendimento Médio por Febre",
                  labels={"Faixa_rendimento": "Rendimento Médio (R$)"})
    st.plotly_chart(fig3, use_container_width=True)

    # --- Conclusões ---
    st.header("📄 Conclusões e Recomendações")
    st.markdown("""
    - ✅ Estados com maiores sintomas devem focar em campanhas de testagem e isolamento.
    - 🚑 Faixas etárias mais idosas concentram internações.
    - 📈 Redução de rendimento está associada à presença de sintomas.
    - ⚖️ Pode haver desigualdade no acesso a testes e internação.
    """)

else:
    st.warning("⚠️ Por favor, envie todos os 4 arquivos para iniciar a análise.")

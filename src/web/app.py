import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns
import os

st.set_page_config(page_title="Passos Mágicos - Student Risk Dashboard", layout="wide")

st.title("🎓 Passos Mágicos - Previsão de Risco de Defasagem")

# API Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Sidebar
st.sidebar.header("Configurações")
year_selected = st.sidebar.selectbox("Selecione o ano para análise estatística", [2022, 2023, 2024])

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Estatísticas Descritivas", "🔮 Predição de Risco", "📈 Performance do Modelo"])

with tab1:
    st.header(f"Estatísticas dos Alunos - {year_selected}")
    
    # Load raw data for summary (simulated or from data/raw)
    try:
        file_path = "data/raw/BASE DE DADOS PEDE 2024 - DATATHON.xlsx"
        sheet_name = f"PEDE{year_selected}"
        df_raw = pd.read_excel(file_path, sheet_name=sheet_name)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Alunos", len(df_raw))
        col2.metric("Média de Idade", f"{df_raw['Idade'].mean() if 'Idade' in df_raw.columns else df_raw['Idade 22'].mean():.1f}")
        
        st.subheader("Distribuição por Gênero")
        fig, ax = plt.subplots()
        gender_col = 'Gênero' if 'Gênero' in df_raw.columns else 'Gênero'
        sns.countplot(data=df_raw, x=gender_col, ax=ax, palette="viridis")
        st.pyplot(fig)
        
    except Exception as e:
        st.warning("Não foi possível carregar os dados brutos para este ano.")

with tab2:
    st.header("Carregar Novos Dados para Predição")
    uploaded_file = st.file_uploader("Escolha um arquivo CSV ou Excel", type=["csv", "xlsx"])
    
    # List models from API
    try:
        response = requests.get(f"{API_URL}/models")
        models = response.json()
        model_names = [m["name"] for m in models]
        selected_model = st.selectbox("Selecione o Modelo", model_names)
    except:
        selected_model = "StudentRiskModel"
        st.error("Conexão com a API falhou. Usando modelo padrão.")

    if uploaded_file is not None:
        if st.button("Executar Predição de Risco"):
            with st.spinner("Processando..."):
                files = {"file": uploaded_file.getvalue()}
                try:
                    res = requests.post(f"{API_URL}/predict/{selected_model}?year={year_selected}", files={"file": (uploaded_file.name, uploaded_file.getvalue())})
                    if res.status_code == 200:
                        results = pd.DataFrame(res.json())
                        st.success("Predição concluída!")
                        st.dataframe(results)
                        
                        # Visualization of risk
                        st.subheader("Distribuição do Risco Predito")
                        fig2, ax2 = plt.subplots()
                        sns.histplot(results['risk_score'], bins=10, kde=True, ax=ax2)
                        st.pyplot(fig2)
                    else:
                        st.error(f"Erro na API: {res.text}")
                except Exception as e:
                    st.error(f"Erro ao conectar com a API: {e}")

with tab3:
    st.header("Métricas de Desempenho (MLflow)")
    st.info("Aqui você pode visualizar as métricas do modelo registrado no MLflow.")
    
    # Simulate some metrics or show MLflow UI link
    st.components.v1.iframe("http://localhost:5000", height=600)

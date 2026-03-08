import streamlit as st

st.set_page_config(
    page_title="Passos Mágicos - Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Plataforma MLOps - Passos Mágicos")
st.markdown("""
### Bem-vindo(a) à Plataforma de Análise de Dados
Utilize o menu lateral para navegar entre as seções:

- **Estatísticas Descritivas:** Análise exploratória e visualização dos dados.
- **Estatísticas Preditivas:** Modelos de Machine Learning e previsões.
- **Atualização de Dados:** Inserção e atualização dos dados da plataforma.
""")

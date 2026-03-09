import streamlit as st
import pandas as pd
import numpy as np
import io
import requests
import os

st.set_page_config(page_title="Estatísticas Preditivas", page_icon="⚙️", layout="wide")

# Configurações de API
API_BASE_URL = "http://localhost:8001"

# Estilo Premium
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stAlert {
        border-radius: 10px;
    }
    .status-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #ffffff;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 Estatísticas Preditivas")
st.markdown("""
Esta página realiza predições consumindo a **API de Predição (FastAPI)**, que por sua vez utiliza o **Model Registry do MLflow** e o **Feast Feature Store**.
""")

# --- FLUXO DE DADOS ---
with st.expander("ℹ️ Entenda o Fluxo de Dados", expanded=False):
    st.markdown("""
    1. **Upload:** Carregue um arquivo CSV ou Excel com os dados dos alunos.
    2. **API Request:** O Streamlit envia o arquivo para a API Central.
    3. **Enriquecimento (Backend):** A API busca features no Feast Online Store.
    4. **Inferência (Backend):** O modelo no MLflow gera as predições.
    5. **Resultados:** O Streamlit exibe os riscos e permite exportação.
    """)

# --- UPLOAD DE ARQUIVOS ---
st.subheader("1. Carregamento de Dados")

# Modelo de Dados para Download
template_data = pd.DataFrame({
    "registro_unico": ["RA-001", "RA-002"],
    "num_idade": [12, 15],
    "cod_genero": [0, 1],
    "flag_bolsa_estudos": [1, 0],
    "num_fase_atual": [3, 5]
})

csv_template = template_data.to_csv(index=False).encode('utf-8')

col_dl1, col_dl2 = st.columns([1, 3])
with col_dl1:
    st.download_button(
        label="📥 Baixar Modelo CSV",
        data=csv_template,
        file_name="modelo_predicao_passos_magicos.csv",
        mime="text/csv",
        help="Baixe este arquivo para usar como base no preenchimento dos dados."
    )

uploaded_file = st.file_uploader("Ou escolha seu próprio arquivo CSV ou Excel", type=["csv", "xlsx"])

REQUIRED_COLUMNS = {
    "registro_unico": "Identificador Único do Aluno",
    "num_idade": "Idade do Aluno",
    "cod_genero": "Gênero (0 ou 1)",
    "flag_bolsa_estudos": "Bolsista (0 ou 1)",
    "num_fase_atual": "Fase Atual (0 a 8)"
}

def validate_data(df):
    errors = []
    missing = [col for col in REQUIRED_COLUMNS.keys() if col not in df.columns]
    if missing:
        errors.append(f"Colunas ausentes: {', '.join(missing)}")
    return errors

if uploaded_file is not None:
    try:
        # Load file for validation and preview
        file_extension = uploaded_file.name.split('.')[-1]
        if file_extension == 'csv':
            df_upload = pd.read_csv(uploaded_file, sep=None, engine='python')
        else:
            df_upload = pd.read_excel(uploaded_file)
            
        st.success("Arquivo carregado com sucesso!")
        
        validation_errors = validate_data(df_upload)
        
        if validation_errors:
            st.error("### ❌ Erros de Validação Encontrados:")
            for err in validation_errors:
                st.write(f"- {err}")
            st.warning("Por favor, corrija o arquivo e tente novamente.")
        else:
            st.success("### ✅ Dados Validados com Sucesso!")
            st.markdown(f"Foram identificados **{len(df_upload)}** registros prontos para análise.")
            
            with st.expander("👀 Visualizar Dados Brutos"):
                st.dataframe(df_upload.head())
            
            # --- SELEÇÃO DE MODELO ---
            st.markdown("---")
            st.subheader("2. Configuração da Predição")
            
            modelo_selecionado = st.selectbox(
                "Selecione o Modelo para Predição:",
                [
                    "Modelo 1: Predição de Defasagem (Acurácia: 92.5%, F1: 0.89)",
                    "Modelo 2: Risco de Evasão/Defasagem (Acurácia: 88.3%, F1: 0.85)",
                    "Modelo 3: Risco Global (Acurácia: 85.6%, F1: 0.82)"
                ]
            )
            
            if st.button("🚀 Executar Predição na API"):
                with st.spinner("Enviando dados para a API de Predição..."):
                    # Mapear seleção para ID
                    model_id = modelo_selecionado.split(":")[0].split()[-1]
                    
                    # Preparar arquivo para envio
                    # Reset buffer to start
                    uploaded_file.seek(0)
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                    
                    try:
                        response = requests.post(f"{API_BASE_URL}/predict/{model_id}", files=files)
                        
                        if response.status_code == 200:
                            predictions = response.json()
                            
                            # Converter resposta em DataFrame
                            df_results = pd.DataFrame(predictions)
                            
                            # Merge ou Join com o upload original para manter as colunas completas
                            # mas aqui vamos apenas mostrar o resultado retornado pela API
                            st.success("### ✅ Predição Concluída!")
                            
                            # Mostrar resultados em destaque
                            st.markdown("#### Resultados da Análise de Risco")
                            
                            def highlight_risco(val):
                                if val == 'Alto Risco': return 'color: #dc3545; font-weight: bold'
                                if val == 'Baixo Risco': return 'color: #28a745; font-weight: bold'
                                return 'color: #6c757d; font-style: italic'

                            styled_df = df_results.head(20).style.applymap(highlight_risco, subset=['predicao'])
                            st.table(styled_df)
                            
                            # Exportação
                            csv_result = df_results.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                label="📥 Baixar Resultados Completos",
                                data=csv_result,
                                file_name="predicoes_api_passos_magicos.csv",
                                mime="text/csv"
                            )
                        else:
                            st.error(f"Erro na API (Status {response.status_code}): {response.text}")
                    except Exception as api_err:
                        st.error(f"Não foi possível conectar à API em {API_BASE_URL}. Verifique se o servidor FastAPI está rodando.")
                        st.exception(api_err)
                    
    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")
else:
    st.info("Aguardando upload de arquivo para iniciar a validação.")

st.markdown("---")
st.caption("Esta plataforma utiliza **FastAPI** como orquestrador, integrando **MLflow** e **Feast**.")

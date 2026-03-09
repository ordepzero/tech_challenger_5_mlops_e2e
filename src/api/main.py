from fastapi import FastAPI, UploadFile, File, HTTPException
import mlflow.sklearn
import pandas as pd
import numpy as np
import os
import traceback
from typing import List, Optional
from pydantic import BaseModel
from feast import FeatureStore
from datetime import datetime
from loguru import logger

# Configuração de Caminhos Absolutos
PROJECT_ROOT = r'D:\arquivos_antigos\Projetos\FIAP\Fase5\tech_challenger_5_project'
ML_DB_PATH = os.path.join(PROJECT_ROOT, 'mlflow.db')
MLFLOW_TRACKING_URI = f"sqlite:///{ML_DB_PATH}"
FEATURE_REPO_PATH = os.path.join(PROJECT_ROOT, 'feature_repo')

# Configurar MLflow
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

app = FastAPI(
    title="Passos Mágicos - API de Predição",
    description="API para predição de risco de desempenho e defasagem de alunos."
)

# Modelos Pydantic para Payload e Resposta
class PredictionResponse(BaseModel):
    registro_unico: str
    predicao: str
    confianca: float

# Cache para Feature Store
def get_feature_store():
    return FeatureStore(repo_path=FEATURE_REPO_PATH)

def load_mlflow_model(model_name: str):
    try:
        model_uri = f"models:/{model_name}/latest"
        logger.info(f"Carregando modelo: {model_uri}")
        return mlflow.sklearn.load_model(model_uri)
    except Exception as e:
        logger.error(f"Erro ao carregar modelo: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Erro ao carregar modelo '{model_name}': {str(e)}")

@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Welcome to the Passos Mágicos Prediction API",
        "documentation": "/docs"
    }

@app.post("/predict/{model_id}", response_model=List[PredictionResponse])
async def predict_file(model_id: int, file: UploadFile = File(...)):
    """
    Realiza predição a partir de um arquivo CSV ou Excel.
    
    - **model_id**: ID do modelo (1, 2 ou 3)
    """
    model_name_map = {
        1: "Passos_Magicos_Modelo_1",
        2: "Passos_Magicos_Modelo_2",
        3: "Passos_Magicos_Modelo_3"
    }
    
    if model_id not in model_name_map:
        raise HTTPException(status_code=400, detail="ID de modelo inválido. Use 1, 2 ou 3.")
        
    model_name = model_name_map[model_id]
    logger.info(f"Iniciando predição para model_id={model_id} ({model_name})")
    
    try:
        # 1. Carregar Dados
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file.file, sep=None, engine='python')
        else:
            df = pd.read_excel(file.file)
            
        if "registro_unico" not in df.columns:
            raise HTTPException(status_code=400, detail="Coluna 'registro_unico' é obrigatória.")

        logger.info(f"Arquivo carregado com {len(df)} registros.")

        # 2. Carregar Modelo
        model = load_mlflow_model(model_name)
        
        # 3. Enriquecimento via Feature Store
        store = get_feature_store()
        entity_df = df[['registro_unico']].copy()
        # Feast requer timezone aware para bater com os dados do offline store (Parquet agora em UTC)
        entity_df['event_timestamp'] = pd.Timestamp.now(tz='UTC').floor('s')
        
        # Features baseadas no modelo (sincronizado com Notebook 06_model)
        model_features_map = {
            1: [
                "student_performance_features:num_idade",
                "student_performance_features:cod_genero",
                "student_performance_features:is_escola_publica",
                "student_performance_features:flag_bolsa_estudos"
            ],
            2: [
                "student_performance_features:num_idade",
                "student_performance_features:flag_bolsa_estudos",
                "student_performance_features:qtd_defasagem"
            ],
            3: [
                "student_performance_features:num_idade",
                "student_performance_features:cod_genero",
                "student_performance_features:flag_bolsa_estudos",
                "student_performance_features:num_fase_atual"
            ]
        }
        
        features_to_fetch = model_features_map[model_id]
        logger.info(f"Buscando features no Feast: {features_to_fetch}")
        
        enriched_df = store.get_historical_features(
            entity_df=entity_df,
            features=features_to_fetch
        ).to_df()
        
        # 4. Inferência
        # Garantir ordem das colunas removendo o event_timestamp e registro_unico
        # E mantendo exatamente a ordem definida na lista de features (removendo o prefixo do view)
        feature_names = [f.split(":")[1] for f in features_to_fetch]
        logger.info(f"Colunas para inferência: {feature_names}")
        
        X = enriched_df[feature_names].fillna(0)
        
        logger.info("Executando inferência do modelo...")
        preds = model.predict(X)
        probs = None
        try:
            # Tenta obter probabilidades
            probs = model.predict_proba(X)[:, 1]
        except Exception as e_prob:
            logger.warning(f"Não foi possível obter predict_proba: {e_prob}")
            probs = np.ones(len(preds)) # Fallback
            
        # 5. Formatar Resposta
        results = []
        for i, p in enumerate(preds):
            results.append(PredictionResponse(
                registro_unico=str(enriched_df.iloc[i]['registro_unico']),
                predicao="Alto Risco" if p == 1 else "Baixo Risco",
                confianca=float(probs[i] * 100) if probs is not None else 100.0
            ))
            
        logger.info("Predição concluída com sucesso.")
        return results
        
    except Exception as e:
        logger.error(f"Erro Crítico: {str(e)}")
        logger.error(traceback.format_exc())
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=f"Erro interno no processamento: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

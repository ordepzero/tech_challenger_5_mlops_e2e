from fastapi import FastAPI, UploadFile, File, HTTPException
import mlflow.sklearn
import pandas as pd
import os
from typing import List, Dict
from pydantic import BaseModel
import sys

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))
from data_preprocessing import preprocess_data

app = FastAPI(title="Student Performance Risk API")

# Path to local MLflow registry (if using local files)
# In a real setup, this would be an environment variable
os.environ['MLFLOW_TRACKING_URI'] = "http://localhost:5000"

class PredictionResponse(BaseModel):
    registro_unico: str
    risk_score: float
    prediction: int

@app.get("/")
def read_root():
    return {"message": "Welcome to the Student Performance Risk API"}

@app.get("/models")
def list_models():
    """Lists available models in the MLflow registry."""
    try:
        from mlflow.tracking import MlflowClient
        client = MlflowClient()
        models = client.search_registered_models()
        return [{"name": m.name, "latest_versions": [v.version for v in m.latest_versions]} for m in models]
    except Exception as e:
        # Fallback if MLflow is not running/accessible
        return [{"name": "StudentRiskModel", "latest_versions": ["1"]}]

@app.post("/predict/{model_name}", response_model=List[PredictionResponse])
async def predict(model_name: str, file: UploadFile = File(...), year: int = 2024):
    """Predicts risk for students in the uploaded CSV/Excel file."""
    try:
        # Load the model from MLflow
        model_uri = f"models:/{model_name}/latest"
        model = mlflow.sklearn.load_model(model_uri)
        
        # Load data
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file.file)
        else:
            df = pd.read_excel(file.file)
            
        # Preprocess
        df_processed = preprocess_data(df, year)
        
        # Features for the model
        features = [
            "num_idade", "cod_genero", "melhor_avaliacao_score", 
            "pior_avaliacao_score", "num_fase_atual", "flag_bolsa_estudos"
        ]
        X = df_processed[features].fillna(0)
        
        # Predict
        probs = model.predict_proba(X)[:, 1]
        preds = model.predict(X)
        
        results = []
        for i, row in df_processed.iterrows():
            results.append(PredictionResponse(
                registro_unico=str(row["registro_unico"]),
                risk_score=float(probs[i]),
                prediction=int(preds[i])
            ))
            
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from feast import FeatureStore
import os
from pathlib import Path
from loguru import logger
import argparse

def train_model(year: int = 2024):
    logger.info(f"Starting model training for year {year}...")
    
    # 1. Initialize Feast Feature Store
    # Assuming we are in the project root
    store = FeatureStore(repo_path="./feature_repo")
    
    # 2. Get historical features for training
    # For simplicity, we'll read the processed parquet directly or use feast's get_historical_features
    # Here we'll simulate the entity dataframe
    entity_df = pd.DataFrame.from_dict({
        "registro_unico": ["RA-1", "RA-2", "RA-861", "RA-862"], # Example IDs
        "event_timestamp": [
            pd.Timestamp("2024-01-01"),
            pd.Timestamp("2024-01-01"),
            pd.Timestamp("2024-01-01"),
            "2024-01-01"
        ]
    })
    
    # In a real setup, we would join features with labels
    # For the purpose of this implementation, we'll load the processed data directly
    # and use it to demonstrate MLflow tracking.
    
    data_path = f"data/processed/year=2026/month=03/day=02/student_performance_{year}.parquet"
    if not os.path.exists(data_path):
        logger.error(f"Processed data not found at {data_path}. Please run the Airflow pipeline first.")
        # Simulating data for demonstration if file doesn't exist
        df = pd.DataFrame({
            "num_idade": [15, 16, 17, 18, 19] * 20,
            "cod_genero": [0, 1] * 50,
            "indic_desenv_educ_22": [7.0, 8.0, 6.5, 9.0, 5.5] * 20,
            "melhor_avaliacao_score": [4, 5, 3, 5, 2] * 20,
            "pior_avaliacao_score": [2, 3, 1, 4, 1] * 20,
            "defasagem_negativa": [0, 0, 1, 0, 1] * 20, # Target
            "num_fase_atual": [5, 6, 7, 8, 9] * 20,
            "flag_bolsa_estudos": [1, 0] * 50
        })
    else:
        df = pd.read_parquet(data_path)

    # 3. Prepare data for modeling
    features = [
        "num_idade", "cod_genero", "melhor_avaliacao_score", 
        "pior_avaliacao_score", "num_fase_atual", "flag_bolsa_estudos"
    ]
    target = "defasagem_negativa"
    
    X = df[features].fillna(0)
    y = df[target].fillna(0)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 4. Train with MLflow tracking
    mlflow.set_experiment("StudentPerformanceRisk")
    
    with mlflow.start_run(run_name=f"RandomForest_{year}"):
        n_estimators = 100
        max_depth = 5
        
        model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, random_state=42)
        model.fit(X_train, y_train)
        
        # Log params
        mlflow.log_param("n_estimators", n_estimators)
        mlflow.log_param("max_depth", max_depth)
        mlflow.log_param("year_base", year)
        
        # Predictions and Metrics
        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        
        mlflow.log_metric("accuracy", acc)
        mlflow.log_metric("f1_score", f1)
        
        logger.info(f"Model trained. Accuracy: {acc:.4f}, F1: {f1:.4f}")
        
        # Log model
        mlflow.sklearn.log_model(model, "model", registered_model_name="StudentRiskModel")
        
        logger.success(f"Run completed and model registered in MLflow.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, default=2024)
    args = parser.parse_args()
    train_model(args.year)

from feast import Entity, FeatureView, Field, FileSource, ValueType
from feast.types import Float32, Int32, String
from datetime import timedelta
import os

# Define the student entity
student = Entity(
    name="student",
    join_keys=["registro_unico"],
    description="Student ID (RA)",
)

# Define the source for student performance features
# Note: In a real Airflow/Feast setup, this would be a dynamic path or a data warehouse.
# For local, we point to the processed parquet.
student_performance_source = FileSource(
    path="/opt/airflow/data/processed/year=2026/month=03/day=02/student_performance_2024.parquet", # Example path
    timestamp_field="event_timestamp", # We need to make sure our preprocessing adds this
    created_timestamp_column="created_timestamp",
)

# Define the feature view
student_performance_fv = FeatureView(
    name="student_performance_features",
    entities=[student],
    ttl=timedelta(days=365*5),
    schema=[
        Field(name="num_idade", dtype=Int32),
        Field(name="cod_genero", dtype=Int32),
        Field(name="indic_desenv_educ_24", dtype=Float32),
        Field(name="melhor_avaliacao_score", dtype=Int32),
        Field(name="pior_avaliacao_score", dtype=Int32),
        Field(name="defasagem_positiva", dtype=Int32),
        Field(name="defasagem_negativa", dtype=Int32),
        Field(name="num_fase_atual", dtype=Int32),
        Field(name="flag_bolsa_estudos", dtype=Int32),
    ],
    online=True,
    source=student_performance_source,
    tags={"team": "analytics"},
)

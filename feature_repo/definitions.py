from feast import Entity, FeatureView, Field, FileSource, ValueType
from feast.types import Int32
from datetime import timedelta

# Define the student entity
student = Entity(
    name="student",
    join_keys=["registro_unico"],
    value_type=ValueType.STRING,
    description="Student ID (RA)",
)

# Define the source for student performance features
# Using relative path from the feature_repo directory
student_performance_source = FileSource(
    path="../data/refined/pede_refined_all.parquet",
    timestamp_field="event_timestamp",
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
        Field(name="melhor_avaliacao_score", dtype=Int32),
        Field(name="pior_avaliacao_score", dtype=Int32),
        Field(name="num_fase_atual", dtype=Int32),
        Field(name="flag_bolsa_estudos", dtype=Int32),
        # Adding some other potential features from prep
        Field(name="is_escola_publica", dtype=Int32),
        Field(name="qtd_defasagem", dtype=Int32),
    ],
    online=True,
    source=student_performance_source,
    tags={"team": "analytics"},
)

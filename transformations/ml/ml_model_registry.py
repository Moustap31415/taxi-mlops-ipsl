from pyspark import pipelines as dp
from pyspark.sql import functions as F

@dp.materialized_view(
    comment="Model metadata and registration information"
)
def ml_model_registry():
    metrics_df = spark.read.table("ml_model_training")

    return (
        metrics_df
        .withColumn("model_name", F.lit("taxi_fare_prediction_model"))
        .withColumn("model_version", F.lit("v1.0"))
        .withColumn("model_status", F.lit("active"))
        .withColumn("catalog", F.lit("taxi_mlops_prod"))
        .withColumn("schema", F.lit("mouhamadou_moustapha_sow"))
        .withColumn("description", F.lit("Linear regression model for taxi fare prediction"))
        .withColumn("registered_at", F.current_timestamp())
        .select(
            "model_name",
            "model_version",
            "model_type",
            "model_status",
            "catalog",
            "schema",
            "rmse",
            "mae",
            "correlation",
            "description",
            "training_timestamp",
            "registered_at"
        )
    )
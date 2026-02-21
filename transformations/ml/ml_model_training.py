from pyspark import pipelines as dp
from pyspark.sql import functions as F

@dp.materialized_view(
    comment="Model training results and evaluation metrics for taxi fare prediction"
)
def ml_model_training():
    df = spark.read.table("ml_training_data")
    
    train_df = df.filter("is_training = true")
    test_df = df.filter("is_training = false")

    train_encoded = (
        train_df
        .withColumn("time_morning", F.when(F.col("time_of_day") == "morning", 1.0).otherwise(0.0))
        .withColumn("time_afternoon", F.when(F.col("time_of_day") == "afternoon", 1.0).otherwise(0.0))
        .withColumn("time_evening", F.when(F.col("time_of_day") == "evening", 1.0).otherwise(0.0))
        .withColumn("time_night", F.when(F.col("time_of_day") == "night", 1.0).otherwise(0.0))
        .withColumn("rush_hour_flag", F.col("is_rush_hour").cast("double"))
        .withColumn("weekend_flag", F.col("is_weekend").cast("double"))
        .withColumn("trip_distance_norm", F.least(F.col("trip_distance") / 50.0, F.lit(1.0)))
        .withColumn("trip_duration_norm", F.least(F.col("trip_duration_minutes") / 120.0, F.lit(1.0)))
        .withColumn("speed_norm", F.least(F.col("speed_mph") / 60.0, F.lit(1.0)))
    )

    predictions = (
        test_df
        .withColumn("time_morning", F.when(F.col("time_of_day") == "morning", 1.0).otherwise(0.0))
        .withColumn("time_afternoon", F.when(F.col("time_of_day") == "afternoon", 1.0).otherwise(0.0))
        .withColumn("time_evening", F.when(F.col("time_of_day") == "evening", 1.0).otherwise(0.0))
        .withColumn("time_night", F.when(F.col("time_of_day") == "night", 1.0).otherwise(0.0))
        .withColumn("rush_hour_flag", F.col("is_rush_hour").cast("double"))
        .withColumn("weekend_flag", F.col("is_weekend").cast("double"))
        .withColumn(
            "predicted_total_amount",
            F.lit(3.0) +
            (F.col("trip_distance") * 2.5) +
            (F.col("trip_duration_minutes") * 0.5) +
            F.when(F.col("time_evening") == 1, 2.0).otherwise(0.0) +
            F.when(F.col("time_night") == 1, 3.0).otherwise(0.0) +
            F.when(F.col("is_rush_hour") == True, 2.0).otherwise(0.0) +
            F.when(F.col("trip_category") == "long", 1.5).otherwise(0.0)
        )
    )

    metrics = predictions.agg(
        F.sqrt(F.avg(F.pow(F.col("predicted_total_amount") - F.col("target_total_amount"), 2))).alias("rmse"),
        F.avg(F.abs(F.col("predicted_total_amount") - F.col("target_total_amount"))).alias("mae"),
        F.corr("predicted_total_amount", "target_total_amount").alias("correlation")
    )

    return metrics.select(
        F.lit("simple_linear_model").alias("model_type"),
        F.col("rmse"),
        F.col("mae"),
        F.col("correlation"),
        F.current_timestamp().alias("training_timestamp")
    )
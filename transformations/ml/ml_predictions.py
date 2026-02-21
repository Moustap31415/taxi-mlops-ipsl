from pyspark import pipelines as dp
from pyspark.sql import functions as F

@dp.materialized_view(
    comment="Batch predictions on 1000 sample taxi trips with actual vs predicted fare comparison"
)
def ml_predictions():
    test_data = (
        spark.read.table("ml_training_data")
        .filter("is_training = false")
        .limit(1000)
    )

    predictions = (
        test_data
        .withColumn("time_morning", F.when(F.col("time_of_day") == "morning", 1.0).otherwise(0.0))
        .withColumn("time_afternoon", F.when(F.col("time_of_day") == "afternoon", 1.0).otherwise(0.0))
        .withColumn("time_evening", F.when(F.col("time_of_day") == "evening", 1.0).otherwise(0.0))
        .withColumn("time_night", F.when(F.col("time_of_day") == "night", 1.0).otherwise(0.0))
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
        .withColumn("prediction_error", F.col("predicted_total_amount") - F.col("target_total_amount"))
        .withColumn("absolute_error", F.abs(F.col("prediction_error")))
        .withColumn("error_percentage", (F.col("absolute_error") / F.col("target_total_amount")) * 100)
    )

    return predictions.select(
        "trip_distance",
        "trip_duration_minutes",
        "speed_mph",
        "pickup_hour",
        "pickup_day_of_week",
        "time_of_day",
        "is_rush_hour",
        "is_weekend",
        "trip_category",
        "pickup_zip",
        "dropoff_zip",
        F.col("target_total_amount").alias("actual_total_amount"),
        "predicted_total_amount",
        "prediction_error",
        "absolute_error",
        "error_percentage"
    )
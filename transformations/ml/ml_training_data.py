from pyspark import pipelines as dp
from pyspark.sql import functions as F

@dp.materialized_view(
    comment="ML training dataset with features for fare amount prediction model"
)
def ml_training_data():
    return (
        spark.read.table("silver_taxi_features")
        .filter("""
            trip_distance > 0 AND trip_distance < 100 AND
            trip_duration_minutes > 0 AND trip_duration_minutes < 180 AND
            fare_amount > 0 AND fare_amount < 500
        """)
        .select(
            # Target variable
            F.col("fare_amount").alias("target_total_amount"),

            # Trip features
            "trip_distance",
            "trip_duration_minutes",
            "speed_mph",

            # Time features
            "pickup_hour",
            "pickup_day_of_week",
            "time_of_day",
            "is_rush_hour",
            "is_weekend",
            "trip_category",

            # Location features
            "pickup_zip",
            "dropoff_zip",

            # Date for partitioning
            "pickup_date"
        )
        .withColumn("is_training", (F.hash("pickup_date", "pickup_zip") % 100) < 80)
    )
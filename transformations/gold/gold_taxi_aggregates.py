from pyspark import pipelines as dp
from pyspark.sql import functions as F

@dp.materialized_view(
    comment="Hourly aggregated taxi metrics by pickup zone for ML model features",
    partition_cols=["pickup_date"]
)
def gold_hourly_location_metrics():
    return (
        spark.read.table("silver_taxi_features")
        .groupBy("pickup_date", "pickup_hour", "pickup_zip")
        .agg(
            F.count("*").alias("trip_count"),
            F.avg("trip_distance").alias("avg_trip_distance"),
            F.avg("trip_duration_minutes").alias("avg_trip_duration"),
            F.avg("fare_amount").alias("avg_fare_amount"),
            F.avg("speed_mph").alias("avg_speed_mph"),
            F.sum("fare_amount").alias("total_revenue")
        )
    )


@dp.materialized_view(
    comment="Daily aggregated taxi metrics by time of day",
    partition_cols=["pickup_date"]
)
def gold_daily_time_patterns():
    return (
        spark.read.table("silver_taxi_features")
        .groupBy("pickup_date", "pickup_day_of_week", "time_of_day")
        .agg(
            F.count("*").alias("trip_count"),
            F.avg("trip_distance").alias("avg_trip_distance"),
            F.avg("trip_duration_minutes").alias("avg_trip_duration"),
            F.avg("fare_amount").alias("avg_fare_amount"),
            F.avg("speed_mph").alias("avg_speed_mph"),
            F.sum("fare_amount").alias("total_revenue"),
            F.sum(F.when(F.col("is_rush_hour") == True, 1).otherwise(0)).alias("rush_hour_trips"),
            F.sum(F.when(F.col("is_weekend") == True, 1).otherwise(0)).alias("weekend_trips")
        )
    )


@dp.materialized_view(
    comment="Location pair metrics for route optimization",
    partition_cols=["pickup_date"]
)
def gold_location_pair_metrics():
    return (
        spark.read.table("silver_taxi_features")
        .groupBy("pickup_date", "pickup_zip", "dropoff_zip")
        .agg(
            F.count("*").alias("route_trip_count"),
            F.avg("trip_distance").alias("avg_route_distance"),
            F.avg("trip_duration_minutes").alias("avg_route_duration"),
            F.avg("fare_amount").alias("avg_route_fare"),
            F.avg("speed_mph").alias("avg_route_speed"),
            F.min("trip_duration_minutes").alias("min_route_duration"),
            F.max("trip_duration_minutes").alias("max_route_duration")
        )
        .filter("route_trip_count >= 5")
    )
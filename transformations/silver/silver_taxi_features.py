from pyspark import pipelines as dp
from pyspark.sql import functions as F

@dp.table(
    comment="Cleaned taxi trip data with engineered features for ML model training"
)
@dp.expect_all_or_drop({
    "valid_trip_distance": "trip_distance > 0 AND trip_distance < 100",
    "valid_fare": "fare_amount > 0 AND fare_amount < 500",
    "valid_passenger_count": "passenger_count > 0 AND passenger_count <= 6",
    "valid_timestamps": "tpep_pickup_datetime < tpep_dropoff_datetime",
    "valid_trip_duration": "trip_duration_minutes > 0 AND trip_duration_minutes < 180",
    "valid_speed": "speed_mph >= 0 AND speed_mph < 150"
})
@dp.expect_all({
    "reasonable_tip": "tip_amount >= 0 AND tip_amount < 100",
    "reasonable_total": "total_amount > 0 AND total_amount < 1000"
})
def silver_taxi_features():
    """
    Silver layer: Feature engineering for ML
    - Cleans and validates raw data
    - Derives time-based features (hour, day of week, time of day)
    - Calculates trip metrics (duration, speed)
    - Identifies special trip types (airport trips)
    - Applies data quality expectations
    """
    return (
        spark.readStream.table("bronze_taxi_trips")
        .filter("VendorID IS NOT NULL")
        
        # Calculate trip duration in minutes
        .withColumn(
            "trip_duration_minutes",
            (F.unix_timestamp("tpep_dropoff_datetime") - 
             F.unix_timestamp("tpep_pickup_datetime")) / 60
        )
        
        # Calculate average speed in mph
        .withColumn(
            "speed_mph",
            F.when(
                F.col("trip_duration_minutes") > 0,
                (F.col("trip_distance") / F.col("trip_duration_minutes")) * 60
            ).otherwise(0)
        )
        
        # Extract time-based features
        .withColumn("pickup_hour", F.hour("tpep_pickup_datetime"))
        .withColumn("pickup_day_of_week", F.dayofweek("tpep_pickup_datetime"))
        .withColumn("pickup_date", F.to_date("tpep_pickup_datetime"))
        
        # Categorize time of day
        .withColumn(
            "time_of_day",
            F.when((F.col("pickup_hour") >= 6) & (F.col("pickup_hour") < 12), "morning")
            .when((F.col("pickup_hour") >= 12) & (F.col("pickup_hour") < 18), "afternoon")
            .when((F.col("pickup_hour") >= 18) & (F.col("pickup_hour") < 22), "evening")
            .otherwise("night")
        )
        
        # Identify airport trips (JFK=132, LaGuardia=138, Newark=1)
        .withColumn(
            "is_airport_pickup",
            F.col("PULocationID").isin([1, 132, 138])
        )
        .withColumn(
            "is_airport_dropoff",
            F.col("DOLocationID").isin([1, 132, 138])
        )
        
        # Feature 1: Rush hour indicator
        # Justification: Les heures de pointe augmentent la durée et le tarif
        .withColumn(
            "is_rush_hour",
            F.when(
                ((F.col("pickup_hour") >= 7) & (F.col("pickup_hour") <= 9)) |
                ((F.col("pickup_hour") >= 17) & (F.col("pickup_hour") <= 19)),
                True
            ).otherwise(False)
        )
        
        # Feature 2: Trip category based on distance
        # Justification: Segmenter les trajets pour améliorer les prédictions
        .withColumn(
            "trip_category",
            F.when(F.col("trip_distance") < 2, "short")
            .when(F.col("trip_distance") < 10, "medium")
            .otherwise("long")
        )
        
        # Feature 3: Weekend indicator
        # Justification: Les patterns de trajet sont différents le weekend
        .withColumn(
            "is_weekend",
            F.when(F.col("pickup_day_of_week").isin([1, 7]), True).otherwise(False)
        )
    )

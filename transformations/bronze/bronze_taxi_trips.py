from pyspark import pipelines as dp
from pyspark.sql import functions as F

@dp.table(
    comment="Raw taxi trip data ingested from cloud storage using Auto Loader"
)
def bronze_taxi_trips():
    """
    Bronze layer: Raw taxi trip data ingestion
    Reads yellow taxi trip data directly from Unity Catalog table
    """
    return (
        spark.readStream.table("taxi_mlops_prod.mouhamadou_moustapha_sow.yellowdata")
    )
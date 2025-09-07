from pyspark.sql import SparkSession
import os
from dotenv import load_dotenv
from pyspark.sql.functions import *
from pyspark.sql.types import *

load_dotenv()

if __name__ == "__main__":

    # The package needs to be specified either here in the config or with --packages
    # Let's add it here to make the script self-contained.
    # Make sure the version matches your PySpark installation.

    spark = SparkSession \
        .builder \
        .appName("Kafka Feedback writer") \
        .master("local[*]") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("ERROR")

    KAFKA_TOPIC_NAME = os.getenv("KAFKA_TOPIC_NAME")
    KAFKA_BOOTSTRAP_SERVER = os.getenv("KAFKA_BOOTSTRAP_SERVER")

    feedbackDF = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVER) \
        .option("subscribe", KAFKA_TOPIC_NAME) \
        .option("startingOffsets", "earliest") \
        .option("failOnDataLoss", "false") \
        .load()

    json_schema = StructType([
        StructField("campaign_id",StringType(),True),
        StructField("user_id",StringType(),True),
        StructField("request_id",StringType(),True),
        StructField("auction_cpm",DoubleType(),True),
        StructField("auction_cpa",DoubleType(),True),
        StructField("auction_cpc",DoubleType(),True),
        StructField("target_age_range",StringType(),True),
        StructField("target_location",StringType(),True),
        StructField("target_gender",StringType(),True),
        StructField("target_income_bucket",StringType(),True),
        StructField("target_device_type",StringType(),True),
        StructField("campaign_start_time",TimestampType(),True),
        StructField("campaign_end_time",TimestampType(),True),
        StructField("expenditure_amount",DoubleType(),True),
        StructField("user_action",StringType(),True),
        StructField("timestamp",TimestampType(),True),
        StructField("click",IntegerType(),True),
        StructField("view",IntegerType(),True),
        StructField("acquisition",IntegerType(),True)
    ])
    desearialised_df = feedbackDF.selectExpr("CAST(value AS STRING) as json_string") \
        .select(from_json(col("json_string"),json_schema).alias("data"))\
        .select("data.*")

    # --- Start Query 1: Writing to JSON files ---
    output_path = os.getenv("FILE_OUTPUT_PATH")
    checkpoint_path = os.getenv("CHECKPOINT_PATH")
    
    file_sink_query = desearialised_df.writeStream \
        .format("json") \
        .option("path", output_path) \
        .option("checkpointLocation", checkpoint_path) \
        .trigger(processingTime="5 seconds") \
        .start()

    # --- Start Query 2: Writing to the console ---
    console_sink_query = desearialised_df.writeStream \
        .format("console") \
        .outputMode("append") \
        .trigger(processingTime="5 seconds") \
        .start()

    # --- Wait for any of the streams to terminate ---
    spark.streams.awaitAnyTermination()

    spark.stop()
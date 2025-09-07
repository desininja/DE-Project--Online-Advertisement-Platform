from pyspark.sql import SparkSession

def main():
    # Create a SparkSession
    spark = SparkSession.builder \
        .appName("MyFirstSparkApp") \
        .master("local[*]") \
        .getOrCreate()

    print(f"Spark version: {spark.version}")

    # Create a sample DataFrame
    data = [("Alice", 34),
            ("Bob", 45),
            ("Catherine", 29)]

    columns = ["name", "age"]
    df = spark.createDataFrame(data, columns)

    print("Sample DataFrame:")
    df.show()

    # Stop the SparkSession
    spark.stop()
    print("Spark session stopped.")

if __name__ == "__main__":
    main()
"""
Meteor - PySpark Processing Pipeline
CSV -> Validation -> Cleaning -> Deduplication -> Transformation -> Parquet
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, year, month

spark = SparkSession.builder.appName("MeteorSparkPipeline").getOrCreate()

print("=== STEP 1: READ RAW CSV ===")
df = spark.read.csv("data/orders.csv", header=True, inferSchema=True)
print(f"Raw row count: {df.count()}")

print("\n=== STEP 2: VALIDATION (remove invalid order_amount) ===")
validated_df = df.filter(col("order_amount") >= 0)
print(f"Rows after validation: {validated_df.count()}")

print("\n=== STEP 3: CLEANING (drop rows with nulls in critical fields) ===")
cleaned_df = validated_df.dropna(subset=["order_id", "customer_id", "order_amount"])
print(f"Rows after cleaning: {cleaned_df.count()}")

print("\n=== STEP 4: DEDUPLICATION (drop duplicate order_id) ===")
deduped_df = cleaned_df.dropDuplicates(["order_id"])
print(f"Rows after deduplication: {deduped_df.count()}")

print("\n=== STEP 5: TRANSFORMATION (add order_year, order_month) ===")
transformed_df = deduped_df.withColumn("order_year", year(col("order_date"))) \
                            .withColumn("order_month", month(col("order_date")))
transformed_df.show(5)

print("\n=== STEP 6: WRITE TO PARQUET ===")
transformed_df.write.mode("overwrite").parquet("data/processed/orders_parquet")
print("Written to data/processed/orders_parquet")

spark.stop()
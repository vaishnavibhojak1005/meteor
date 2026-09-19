"""
Meteor - PySpark Processing Pipeline (with Quarantine)
CSV -> Validation (split valid/invalid) -> Cleaning -> Deduplication
-> Transformation -> Parquet, with invalid rows quarantined.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, year, month, lit, when

spark = SparkSession.builder.appName("MeteorSparkPipeline").getOrCreate()

print("=== STEP 1: READ RAW CSV ===")
df = spark.read.csv("data/orders.csv", header=True, inferSchema=True)
print(f"Raw row count: {df.count()}")

print("\n=== STEP 2: VALIDATION (split valid/invalid) ===")
invalid_df = df.filter(col("order_amount") < 0) \
               .withColumn("quarantine_reason", lit("negative_order_amount"))
valid_df = df.filter(col("order_amount") >= 0)

print(f"Valid rows: {valid_df.count()}")
print(f"Invalid rows (quarantined): {invalid_df.count()}")

if invalid_df.count() > 0:
    invalid_df.write.mode("overwrite").parquet("data/quarantine/orders_invalid")
    print("Quarantined rows written to data/quarantine/orders_invalid")

print("\n=== STEP 3: CLEANING (drop rows with nulls in critical fields) ===")
cleaned_df = valid_df.dropna(subset=["order_id", "customer_id", "order_amount"])
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
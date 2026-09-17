"""
Meteor - PySpark First Test
Reads orders.csv using Spark and performs basic operations,
demonstrating lazy evaluation and the DataFrame API.
"""

from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("MeteorSparkTest").getOrCreate()

df = spark.read.csv("data/orders.csv", header=True, inferSchema=True)

print("=== SCHEMA (Spark inferred this automatically) ===")
df.printSchema()

print("\n=== ROW COUNT ===")
print(f"Total rows: {df.count()}")

print("\n=== FIRST 5 ROWS ===")
df.show(5)

spark.stop()
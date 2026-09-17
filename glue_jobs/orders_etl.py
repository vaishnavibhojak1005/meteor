"""
Meteor - Glue ETL Job
Reads orders.csv from S3 raw/, validates and transforms it,
writes Parquet output to S3 processed/.
"""

import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col, year, month

args = getResolvedOptions(sys.argv, ["JOB_NAME"])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

RAW_PATH = "s3://meteor-data-lake-397781772486/raw/orders.csv"
PROCESSED_PATH = "s3://meteor-data-lake-397781772486/processed/orders_parquet"

df = spark.read.csv(RAW_PATH, header=True, inferSchema=True)
print(f"Raw row count: {df.count()}")

validated_df = df.filter(col("order_amount") >= 0)
cleaned_df = validated_df.dropna(subset=["order_id", "customer_id", "order_amount"])
deduped_df = cleaned_df.dropDuplicates(["order_id"])

transformed_df = deduped_df.withColumn("order_year", year(col("order_date"))) \
                            .withColumn("order_month", month(col("order_date")))

print(f"Final row count: {transformed_df.count()}")

transformed_df.write.mode("overwrite").parquet(PROCESSED_PATH)
print(f"Written to {PROCESSED_PATH}")

job.commit()
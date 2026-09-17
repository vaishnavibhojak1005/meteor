CREATE EXTERNAL TABLE meteor_db.orders_processed (
  order_id INT,
  customer_id INT,
  product_id INT,
  order_amount DOUBLE,
  order_date TIMESTAMP,
  payment_status STRING,
  city STRING,
  order_year INT,
  order_month INT
)
STORED AS PARQUET
LOCATION 's3://meteor-data-lake-397781772486/processed/orders_parquet/'

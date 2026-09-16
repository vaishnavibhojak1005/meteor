"""
Meteor - FastAPI Backend
Exposes Meteor's data quality and incident data via a REST API.
"""

import psycopg2
import psycopg2.extras
import pandas as pd
from fastapi import FastAPI, HTTPException

from quality_engine.quality import (
    check_allowed_values,
    check_completeness,
    check_duplicates,
    check_freshness,
    check_schema,
    check_validity,
    calculate_quality_score,
    load_weights,
)
from anomaly_engine.statistical import detect_volume_anomaly

app = FastAPI(title="Meteor API", version="0.1.0")

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "meteor_db",
    "user": "meteor_admin",
    "password": "meteor_dev_password",
}

ORDERS_BASELINE_SCHEMA = {
    "order_id": "int64",
    "customer_id": "int64",
    "product_id": "int64",
    "order_amount": "float64",
    "order_date": "str",
    "payment_status": "str",
    "city": "str",
}

ALLOWED_PAYMENT_STATUSES = ["SUCCESS", "FAILED", "PENDING"]


def get_connection():
    """Create a new database connection."""
    return psycopg2.connect(**DB_CONFIG)


@app.get("/health")
def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "service": "Meteor API"}


@app.get("/datasets")
def get_datasets():
    """Return all registered datasets."""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM datasets ORDER BY dataset_id;")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return {"datasets": rows}


@app.get("/datasets/{dataset_id}")
def get_dataset_by_id(dataset_id: int):
    """Return a single dataset by its ID."""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM datasets WHERE dataset_id = %s;", (dataset_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")

    return row


@app.get("/datasets/{dataset_id}/quality")
def get_dataset_quality(dataset_id: int):
    """Run quality checks on a dataset and return the results."""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM datasets WHERE dataset_id = %s;", (dataset_id,))
    dataset = cursor.fetchone()
    cursor.close()
    conn.close()

    if dataset is None:
        raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")

    dataset_name = dataset["name"]
    file_path = f"data/{dataset_name}.csv"

    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Data file not found: {file_path}")

    completeness_result = check_completeness(df)
    duplicates_result = check_duplicates(df, primary_key="order_id")
    validity_result = check_validity(df, "order_amount")
    allowed_values_result = check_allowed_values(df, "payment_status", ALLOWED_PAYMENT_STATUSES)
    freshness_result = check_freshness(df, "order_date")
    schema_result = check_schema(df, ORDERS_BASELINE_SCHEMA)

    weights = load_weights()
    score = calculate_quality_score(
        completeness_result,
        duplicates_result,
        validity_result,
        allowed_values_result,
        freshness_result,
        schema_result,
        weights,
    )

    return {
        "dataset": dataset_name,
        "record_count": len(df),
        "completeness": completeness_result,
        "duplicates": duplicates_result,
        "validity": validity_result,
        "allowed_values": allowed_values_result,
        "freshness": freshness_result,
        "schema": schema_result,
        "quality_score": score,
    }


@app.get("/datasets/{dataset_id}/anomalies")
def get_dataset_anomalies(dataset_id: int):
    """Check a dataset's current volume against its historical baseline."""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM datasets WHERE dataset_id = %s;", (dataset_id,))
    dataset = cursor.fetchone()
    cursor.close()
    conn.close()

    if dataset is None:
        raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")

    dataset_name = dataset["name"]
    file_path = f"data/{dataset_name}.csv"

    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Data file not found: {file_path}")

    current_record_count = len(df)
    anomaly_result = detect_volume_anomaly(dataset_name, current_record_count)

    return anomaly_result
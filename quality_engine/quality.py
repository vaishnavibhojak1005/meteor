"""
Meteor - Data Quality Engine
Runs quality checks against a dataset: completeness, duplicates,
validity, allowed values, freshness, and schema drift.
"""

from datetime import datetime

import pandas as pd


def check_completeness(df: pd.DataFrame) -> dict:
    """Check completeness (null percentage) per column and overall."""
    total_rows = len(df)
    per_column = {}

    for col in df.columns:
        null_count = int(df[col].isnull().sum())
        null_percentage = round((null_count / total_rows) * 100, 2) if total_rows else 0.0
        per_column[col] = {
            "null_count": null_count,
            "null_percentage": null_percentage,
        }

    overall_completeness = round(
        100 - (sum(v["null_percentage"] for v in per_column.values()) / len(per_column)),
        2,
    ) if per_column else 100.0

    return {
        "per_column": per_column,
        "overall_completeness_score": overall_completeness,
    }


def check_duplicates(df: pd.DataFrame, primary_key: str) -> dict:
    """Check for duplicate values in the primary key column."""
    total_rows = len(df)
    unique_count = int(df[primary_key].nunique())
    duplicate_count = total_rows - unique_count
    duplicate_percentage = round((duplicate_count / total_rows) * 100, 2) if total_rows else 0.0

    return {
        "primary_key": primary_key,
        "total_rows": total_rows,
        "unique_count": unique_count,
        "duplicate_count": duplicate_count,
        "duplicate_percentage": duplicate_percentage,
        "status": "PASS" if duplicate_count == 0 else "FAIL",
    }


def check_validity(df: pd.DataFrame, column: str, min_value: float = 0) -> dict:
    """Check that numeric values in a column are >= min_value."""
    series = pd.to_numeric(df[column], errors="coerce")
    invalid_mask = series < min_value
    invalid_count = int(invalid_mask.sum())
    total_rows = len(df)

    return {
        "column": column,
        "invalid_count": invalid_count,
        "invalid_percentage": round((invalid_count / total_rows) * 100, 2) if total_rows else 0.0,
        "status": "PASS" if invalid_count == 0 else "FAIL",
    }


def check_allowed_values(df: pd.DataFrame, column: str, allowed: list) -> dict:
    """Check that all non-null values in a column are within an allowed set."""
    non_null = df[column].dropna()
    invalid_mask = ~non_null.isin(allowed)
    invalid_count = int(invalid_mask.sum())
    total_rows = len(df)

    return {
        "column": column,
        "allowed_values": allowed,
        "invalid_count": invalid_count,
        "invalid_percentage": round((invalid_count / total_rows) * 100, 2) if total_rows else 0.0,
        "status": "PASS" if invalid_count == 0 else "FAIL",
    }


def check_freshness(df: pd.DataFrame, timestamp_column: str, max_delay_hours: int = 48) -> dict:
    """Check whether the latest timestamp is within an acceptable delay from now."""
    parsed = pd.to_datetime(df[timestamp_column], errors="coerce").dropna()
    latest = parsed.max()
    now = pd.Timestamp(datetime.now())
    delay_hours = round((now - latest).total_seconds() / 3600, 2)

    return {
        "column": timestamp_column,
        "latest_timestamp": str(latest),
        "delay_hours": delay_hours,
        "max_allowed_hours": max_delay_hours,
        "status": "PASS" if delay_hours <= max_delay_hours else "FAIL",
    }


def check_schema(df: pd.DataFrame, expected_schema: dict) -> dict:
    """Compare the current DataFrame's schema against an expected baseline."""
    current_schema = {col: str(dtype) for col, dtype in df.dtypes.items()}

    missing_columns = [col for col in expected_schema if col not in current_schema]
    extra_columns = [col for col in current_schema if col not in expected_schema]
    type_mismatches = {
        col: {"expected": expected_schema[col], "actual": current_schema[col]}
        for col in expected_schema
        if col in current_schema and expected_schema[col] != current_schema[col]
    }

    has_drift = bool(missing_columns or extra_columns or type_mismatches)

    return {
        "missing_columns": missing_columns,
        "extra_columns": extra_columns,
        "type_mismatches": type_mismatches,
        "status": "FAIL" if has_drift else "PASS",
    }


if __name__ == "__main__":
    ORDERS_BASELINE_SCHEMA = {
        "order_id": "int64",
        "customer_id": "int64",
        "product_id": "int64",
        "order_amount": "float64",
        "order_date": "str",
        "payment_status": "str",
        "city": "str",
    }

    print("=== VALIDITY: clean vs invalid_orders.csv ===")
    df_clean = pd.read_csv("data/orders.csv")
    df_invalid = pd.read_csv("data/invalid_orders.csv")
    print("Clean:  ", check_validity(df_clean, "order_amount"))
    print("Invalid:", check_validity(df_invalid, "order_amount"))

    print("\n=== ALLOWED VALUES: payment_status ===")
    allowed_statuses = ["SUCCESS", "FAILED", "PENDING"]
    print("Clean:", check_allowed_values(df_clean, "payment_status", allowed_statuses))

    print("\n=== FRESHNESS: clean vs freshness_anomaly_orders.csv ===")
    df_fresh_check = pd.read_csv("data/orders.csv")
    df_stale = pd.read_csv("data/freshness_anomaly_orders.csv")
    print("Clean:", check_freshness(df_fresh_check, "order_date"))
    print("Stale:", check_freshness(df_stale, "order_date"))

    print("\n=== SCHEMA: clean vs schema_drift_orders.csv ===")
    df_drift = pd.read_csv("data/schema_drift_orders.csv")
    print("Clean:", check_schema(df_clean, ORDERS_BASELINE_SCHEMA))
    print("Drift:", check_schema(df_drift, ORDERS_BASELINE_SCHEMA))
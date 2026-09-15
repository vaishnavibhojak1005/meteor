"""
Meteor - Data Quality Engine
Runs quality checks against a dataset: completeness and
duplicate detection (more checks added incrementally).
"""

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


if __name__ == "__main__":
    print("=== TESTING ON CLEAN DATA ===")
    df_clean = pd.read_csv("data/orders.csv")

    completeness = check_completeness(df_clean)
    print(f"Overall completeness: {completeness['overall_completeness_score']}%")

    duplicates = check_duplicates(df_clean, primary_key="order_id")
    print(f"Duplicates: {duplicates['status']} ({duplicates['duplicate_count']} duplicates)")

    print("\n=== TESTING ON NULL-CORRUPTED DATA ===")
    df_null = pd.read_csv("data/null_anomaly_orders.csv")
    completeness_null = check_completeness(df_null)
    print(f"Overall completeness: {completeness_null['overall_completeness_score']}%")
    print(f"payment_status nulls: {completeness_null['per_column']['payment_status']}")

    print("\n=== TESTING ON DUPLICATE-CORRUPTED DATA ===")
    df_dup = pd.read_csv("data/duplicate_anomaly_orders.csv")
    duplicates_dup = check_duplicates(df_dup, primary_key="order_id")
    print(f"Duplicates: {duplicates_dup['status']} ({duplicates_dup['duplicate_count']} duplicates, {duplicates_dup['duplicate_percentage']}%)")
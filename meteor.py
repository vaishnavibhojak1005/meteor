"""
Meteor - Command Line Interface
Runs the data quality engine against a dataset and prints a report.
"""

import argparse

import pandas as pd

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


def run_quality_checks(dataset_path: str) -> None:
    df = pd.read_csv(dataset_path)
    dataset_name = dataset_path.split("/")[-1].replace(".csv", "")

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

    print("=" * 40)
    print("               METEOR")
    print("=" * 40)
    print(f"\nDataset:\n{dataset_name}")
    print(f"\nRecords:\n{len(df)}")
    print(f"\nQuality Score:\n{score['overall_quality_score']}%")
    print("\nChecks")
    print("-" * 40)
    print(f"Completeness       {completeness_result_status(completeness_result)}")
    print(f"Duplicates         {duplicates_result['status']}")
    print(f"Validity           {validity_result['status']}")
    print(f"Freshness          {freshness_result['status']}")
    print(f"Schema             {schema_result['status']}")
    print("-" * 40)
    print(f"\nOverall Status:\n{score['overall_status']}")


def completeness_result_status(completeness_result: dict) -> str:
    """Completeness doesn't have a built-in PASS/FAIL; derive one at 95% threshold."""
    return "PASS" if completeness_result["overall_completeness_score"] >= 95 else "FAIL"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Meteor - Data Quality CLI")
    parser.add_argument("--dataset", required=True, help="Path to the CSV dataset to check")
    args = parser.parse_args()

    run_quality_checks(args.dataset)
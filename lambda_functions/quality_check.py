"""
Meteor - Quality Check Lambda
Triggered by S3 upload. Downloads the CSV and runs lightweight
quality checks (no pandas dependency, to keep the Lambda simple).
"""

import csv
import io
import json

import boto3

s3 = boto3.client("s3")


def run_quality_checks(rows: list, fieldnames: list) -> dict:
    """Run basic completeness and row-count checks on raw CSV rows."""
    total_rows = len(rows)
    null_counts = {field: 0 for field in fieldnames}

    for row in rows:
        for field in fieldnames:
            if row.get(field, "") == "":
                null_counts[field] += 1

    completeness = {
        field: {
            "null_count": null_counts[field],
            "null_percentage": round((null_counts[field] / total_rows) * 100, 2) if total_rows else 0.0,
        }
        for field in fieldnames
    }

    return {
        "record_count": total_rows,
        "completeness": completeness,
    }


def handler(event, context):
    for record in event.get("Records", []):
        bucket_name = record["s3"]["bucket"]["name"]
        object_key = record["s3"]["object"]["key"]

        print(f"Processing: {object_key} from {bucket_name}")

        response = s3.get_object(Bucket=bucket_name, Key=object_key)
        content = response["Body"].read().decode("utf-8")

        reader = csv.DictReader(io.StringIO(content))
        rows = list(reader)
        fieldnames = reader.fieldnames or []

        result = run_quality_checks(rows, fieldnames)

        print("Quality check result:")
        print(json.dumps(result))

    return {
        "statusCode": 200,
        "body": "Quality check complete"
    }
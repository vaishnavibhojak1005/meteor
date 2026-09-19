"""
Meteor - Data Quality Engine Tests
Verifies each quality check correctly distinguishes clean data
from the specific corruption type it's designed to catch.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pandas as pd
import pytest

from quality_engine.quality import (
    check_completeness,
    check_duplicates,
    check_validity,
    check_allowed_values,
    check_freshness,
    check_schema,
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


@pytest.fixture
def clean_orders():
    return pd.read_csv("data/orders.csv")


@pytest.fixture
def null_anomaly_orders():
    return pd.read_csv("data/null_anomaly_orders.csv")


@pytest.fixture
def duplicate_anomaly_orders():
    return pd.read_csv("data/duplicate_anomaly_orders.csv")


@pytest.fixture
def invalid_orders():
    return pd.read_csv("data/invalid_orders.csv")


@pytest.fixture
def schema_drift_orders():
    return pd.read_csv("data/schema_drift_orders.csv")


def test_completeness_passes_on_clean_data(clean_orders):
    result = check_completeness(clean_orders)
    assert result["overall_completeness_score"] == 100.0


def test_completeness_detects_nulls(null_anomaly_orders):
    result = check_completeness(null_anomaly_orders)
    assert result["overall_completeness_score"] < 100.0


def test_duplicates_passes_on_clean_data(clean_orders):
    result = check_duplicates(clean_orders, primary_key="order_id")
    assert result["status"] == "PASS"
    assert result["duplicate_count"] == 0


def test_duplicates_detects_duplicate_rows(duplicate_anomaly_orders):
    result = check_duplicates(duplicate_anomaly_orders, primary_key="order_id")
    assert result["status"] == "FAIL"
    assert result["duplicate_count"] > 0


def test_validity_passes_on_clean_data(clean_orders):
    result = check_validity(clean_orders, "order_amount")
    assert result["status"] == "PASS"


def test_validity_detects_negative_amounts(invalid_orders):
    result = check_validity(invalid_orders, "order_amount")
    assert result["status"] == "FAIL"
    assert result["invalid_count"] == 50


def test_allowed_values_passes_on_clean_data(clean_orders):
    result = check_allowed_values(clean_orders, "payment_status", ["SUCCESS", "FAILED", "PENDING"])
    assert result["status"] == "PASS"


def test_schema_passes_on_clean_data(clean_orders):
    result = check_schema(clean_orders, ORDERS_BASELINE_SCHEMA)
    assert result["status"] == "PASS"
    assert result["type_mismatches"] == {}


def test_schema_detects_drift(schema_drift_orders):
    result = check_schema(schema_drift_orders, ORDERS_BASELINE_SCHEMA)
    assert result["status"] == "FAIL"
    assert "order_amount" in result["type_mismatches"]
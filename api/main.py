"""
Meteor - FastAPI Backend
Exposes Meteor's data quality and incident data via a REST API.
"""
import os
from dotenv import load_dotenv
load_dotenv()
import psycopg2
import psycopg2.extras
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from lineage.lineage_manager import get_full_downstream_impact, get_dataset_name

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

from quality_engine.profiler import (
    profile_structure,
    profile_nulls,
    profile_unique_values,
    profile_numeric_stats,
    profile_timestamp_columns,
)

from anomaly_engine.statistical import detect_volume_anomaly

from incident_engine.incident_manager import (
    create_incident,
    get_all_incidents,
    get_incident_by_id,
    acknowledge_incident,
    resolve_incident,
)


app = FastAPI(
    title="Meteor API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
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


ALLOWED_PAYMENT_STATUSES = [
    "SUCCESS",
    "FAILED",
    "PENDING",
]


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def clean_row(row: dict):
    """Convert database-specific values into JSON-safe values."""

    if row is None:
        return None

    cleaned = {}

    for key, value in row.items():

        if hasattr(value, "isoformat"):
            cleaned[key] = value.isoformat()

        elif str(type(value)) == "<class 'decimal.Decimal'>":
            cleaned[key] = float(value)

        else:
            cleaned[key] = value

    return cleaned


class IncidentCreateRequest(BaseModel):
    dataset_id: int
    incident_type: str
    severity: str
    expected: float
    actual: float
    deviation: float
    root_cause: str = "Not yet determined"
    confidence: float = 0.0


@app.get("/health")
def health_check():
    """Simple health check endpoint."""

    return {
        "status": "ok",
        "service": "Meteor API",
    }


@app.get("/datasets")
def get_datasets():
    """Return all registered datasets."""

    conn = get_connection()

    cursor = conn.cursor(
        cursor_factory=psycopg2.extras.RealDictCursor
    )

    cursor.execute(
        "SELECT * FROM datasets ORDER BY dataset_id;"
    )

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return {
        "datasets": [
            dict(row)
            for row in rows
        ]
    }


@app.get("/datasets/{dataset_id}")
def get_dataset_by_id(dataset_id: int):
    """Return a single dataset by its ID."""

    conn = get_connection()

    cursor = conn.cursor(
        cursor_factory=psycopg2.extras.RealDictCursor
    )

    cursor.execute(
        "SELECT * FROM datasets WHERE dataset_id = %s;",
        (dataset_id,),
    )

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail=f"Dataset {dataset_id} not found",
        )

    return clean_row(dict(row))


def _load_dataset_or_404(dataset_id: int) -> dict:
    """Look up a dataset by ID or raise 404."""

    conn = get_connection()

    cursor = conn.cursor(
        cursor_factory=psycopg2.extras.RealDictCursor
    )

    cursor.execute(
        "SELECT * FROM datasets WHERE dataset_id = %s;",
        (dataset_id,),
    )

    dataset = cursor.fetchone()

    cursor.close()
    conn.close()

    if dataset is None:
        raise HTTPException(
            status_code=404,
            detail=f"Dataset {dataset_id} not found",
        )

    return dict(dataset)


def _load_dataset_csv(dataset_name: str) -> pd.DataFrame:
    """Load a dataset CSV file."""

    file_path = f"data/{dataset_name}.csv"

    try:
        return pd.read_csv(file_path)

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Data file not found: {file_path}",
        )


@app.get("/datasets/{dataset_id}/profile")
def get_dataset_profile(dataset_id: int):
    """Return structural profiling information."""

    dataset = _load_dataset_or_404(dataset_id)

    df = _load_dataset_csv(dataset["name"])

    structure = profile_structure(df)

    nulls = profile_nulls(df)

    uniques = profile_unique_values(df)

    numeric_stats = profile_numeric_stats(df)

    timestamp_info = profile_timestamp_columns(
        df,
        timestamp_columns=["order_date"],
    )

    return {
        "dataset": dataset["name"],
        "structure": structure,
        "nulls": nulls,
        "unique_values": uniques,
        "numeric_stats": numeric_stats,
        "timestamp_info": timestamp_info,
    }


@app.get("/datasets/{dataset_id}/quality")
def get_dataset_quality(dataset_id: int):
    """Run all data quality checks."""

    dataset = _load_dataset_or_404(dataset_id)

    df = _load_dataset_csv(dataset["name"])

    completeness_result = check_completeness(df)

    duplicates_result = check_duplicates(
        df,
        primary_key="order_id",
    )

    validity_result = check_validity(
        df,
        "order_amount",
    )

    allowed_values_result = check_allowed_values(
        df,
        "payment_status",
        ALLOWED_PAYMENT_STATUSES,
    )

    freshness_result = check_freshness(
        df,
        "order_date",
    )

    schema_result = check_schema(
        df,
        ORDERS_BASELINE_SCHEMA,
    )

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
        "dataset": dataset["name"],
        "record_count": len(df),
        "completeness": completeness_result,
        "duplicates": duplicates_result,
        "validity": validity_result,
        "allowed_values": allowed_values_result,
        "freshness": freshness_result,
        "schema": schema_result,
        "quality_score": score,
    }


@app.get("/datasets/{dataset_id}/schema")
def get_dataset_schema(dataset_id: int):
    """Return schema drift check results."""

    dataset = _load_dataset_or_404(dataset_id)

    df = _load_dataset_csv(dataset["name"])

    schema_result = check_schema(
        df,
        ORDERS_BASELINE_SCHEMA,
    )

    return {
        "dataset": dataset["name"],
        "schema_check": schema_result,
    }


@app.get("/datasets/{dataset_id}/anomalies")
def get_dataset_anomalies(dataset_id: int):
    """Check current dataset volume against its historical baseline."""

    dataset = _load_dataset_or_404(dataset_id)

    df = _load_dataset_csv(dataset["name"])

    current_record_count = len(df)

    anomaly_result = detect_volume_anomaly(
        dataset["name"],
        current_record_count,
    )

    return anomaly_result


@app.get("/incidents")
def list_incidents():
    """Return all incidents."""

    incidents = get_all_incidents()

    return {
        "incidents": [
            clean_row(dict(incident))
            for incident in incidents
        ]
    }


@app.get("/incidents/{incident_id}")
def get_incident(incident_id: str):
    """Return a single incident."""

    incident = get_incident_by_id(incident_id)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail=f"Incident {incident_id} not found",
        )

    return clean_row(dict(incident))


@app.post("/incidents")
def create_new_incident(
    payload: IncidentCreateRequest,
):
    """Create a new incident."""

    try:

        incident = create_incident(
            dataset_id=payload.dataset_id,
            incident_type=payload.incident_type,
            severity=payload.severity,
            expected=payload.expected,
            actual=payload.actual,
            deviation=payload.deviation,
            root_cause=payload.root_cause,
            confidence=payload.confidence,
        )

    except psycopg2.errors.ForeignKeyViolation:

        raise HTTPException(
            status_code=400,
            detail=f"dataset_id {payload.dataset_id} does not exist",
        )

    return clean_row(dict(incident))


@app.post("/incidents/{incident_id}/acknowledge")
def acknowledge_incident_endpoint(
    incident_id: str,
):
    """Mark an incident as ACKNOWLEDGED."""

    result = acknowledge_incident(incident_id)

    if "error" in result:

        raise HTTPException(
            status_code=404,
            detail=result["error"],
        )

    return clean_row(dict(result))


@app.post("/incidents/{incident_id}/resolve")
def resolve_incident_endpoint(
    incident_id: str,
):
    """Mark an incident as RESOLVED."""

    result = resolve_incident(incident_id)

    if "error" in result:

        raise HTTPException(
            status_code=404,
            detail=result["error"],
        )

    return clean_row(dict(result))

@app.get("/datasets/{dataset_id}/lineage")
def get_dataset_lineage(dataset_id: int):
    """Return all downstream datasets affected if this dataset fails."""
    dataset_name = get_dataset_name(dataset_id)
    if dataset_name == "UNKNOWN":
        raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")

    downstream = get_full_downstream_impact(dataset_id)

    return {
        "dataset": dataset_name,
        "downstream_impact": downstream,
        "affected_count": len(downstream),
    }    
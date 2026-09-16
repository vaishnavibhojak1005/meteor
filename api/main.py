"""
Meteor - FastAPI Backend
Exposes Meteor's data quality and incident data via a REST API.
"""

import psycopg2
import psycopg2.extras
from fastapi import FastAPI

app = FastAPI(title="Meteor API", version="0.1.0")

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "meteor_db",
    "user": "meteor_admin",
    "password": "meteor_dev_password",
}


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
"""
Meteor - Incident Manager
Creates and manages incident lifecycle: OPEN -> ACKNOWLEDGED -> RESOLVED.
Incidents are stored in PostgreSQL. Includes retry-with-backoff for
database connections and structured logging of key events.
"""

import logging
import os
import time
from datetime import datetime

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("meteor")

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}


def get_connection(max_retries: int = 3):
    """Create a new database connection, retrying with exponential backoff."""
    last_error = None

    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            if attempt > 0:
                logger.info(f"DB connection recovered on attempt {attempt + 1}")
            return conn
        except psycopg2.OperationalError as e:
            last_error = e
            wait_time = 2 ** attempt
            logger.warning(f"DB connection attempt {attempt + 1} failed. Retrying in {wait_time}s...")
            time.sleep(wait_time)

    logger.error(f"DB connection failed after {max_retries} attempts: {last_error}")
    raise ConnectionError(f"Could not connect to database after {max_retries} attempts: {last_error}")


def generate_incident_id() -> str:
    """Generate the next sequential MET-INC-XXXXX ID based on existing row count."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM incidents;")
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()

    next_number = count + 1
    return f"MET-INC-{next_number:05d}"


def create_incident(
    dataset_id: int,
    incident_type: str,
    severity: str,
    expected: float,
    actual: float,
    deviation: float,
    root_cause: str = "Not yet determined",
    confidence: float = 0.0,
) -> dict:
    """Create a new incident and persist it to PostgreSQL."""
    incident_id = generate_incident_id()

    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(
        """
        INSERT INTO incidents (
            incident_id, dataset_id, incident_type, severity,
            expected, actual, deviation, root_cause, confidence, status
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'OPEN')
        RETURNING *;
        """,
        (incident_id, dataset_id, incident_type, severity, expected, actual, deviation, root_cause, confidence),
    )
    incident = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()

    logger.info(f"incident_created: {incident_id} severity={severity} dataset_id={dataset_id}")

    return incident


def get_all_incidents() -> list:
    """Return all incidents, most recent first."""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM incidents ORDER BY created_at DESC;")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_incident_by_id(incident_id: str) -> dict:
    """Return a single incident by its ID, or None if not found."""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM incidents WHERE incident_id = %s;", (incident_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def acknowledge_incident(incident_id: str) -> dict:
    """Mark an incident as ACKNOWLEDGED."""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(
        """
        UPDATE incidents
        SET status = 'ACKNOWLEDGED', acknowledged_at = %s
        WHERE incident_id = %s
        RETURNING *;
        """,
        (datetime.now(), incident_id),
    )
    row = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()

    if row:
        logger.info(f"incident_acknowledged: {incident_id}")

    return row if row else {"error": f"Incident {incident_id} not found"}


def resolve_incident(incident_id: str) -> dict:
    """Mark an incident as RESOLVED."""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(
        """
        UPDATE incidents
        SET status = 'RESOLVED', resolved_at = %s
        WHERE incident_id = %s
        RETURNING *;
        """,
        (datetime.now(), incident_id),
    )
    row = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()

    if row:
        logger.info(f"incident_resolved: {incident_id}")

    return row if row else {"error": f"Incident {incident_id} not found"}


if __name__ == "__main__":
    from severity import calculate_severity

    print("=== CREATING INCIDENT (matching plan's example scenario) ===")
    deviation = -71.67
    severity = calculate_severity(deviation)

    incident = create_incident(
        dataset_id=1,
        incident_type="VOLUME_ANOMALY",
        severity=severity,
        expected=1200000,
        actual=340000,
        deviation=deviation,
    )
    print(dict(incident))

    print("\n=== ACKNOWLEDGING INCIDENT ===")
    acknowledged = acknowledge_incident(incident["incident_id"])
    print(f"Status: {acknowledged['status']}, acknowledged_at: {acknowledged['acknowledged_at']}")

    print("\n=== RESOLVING INCIDENT ===")
    resolved = resolve_incident(incident["incident_id"])
    print(f"Status: {resolved['status']}, resolved_at: {resolved['resolved_at']}")

    print("\n=== LISTING ALL INCIDENTS ===")
    all_incidents = get_all_incidents()
    print(f"Total incidents: {len(all_incidents)}")
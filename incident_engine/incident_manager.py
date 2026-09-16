"""
Meteor - Incident Manager
Creates and manages incident lifecycle: OPEN -> ACKNOWLEDGED -> RESOLVED.
Incidents are stored in PostgreSQL.
"""

import psycopg2
import psycopg2.extras
from datetime import datetime

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
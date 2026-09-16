"""
Meteor - Incident Manager
Creates and manages incident lifecycle: OPEN -> ACKNOWLEDGED -> RESOLVED.
Incidents are stored in a local JSON file for now (Phase 12 will
migrate this to PostgreSQL).
"""

import json
import os
from datetime import datetime

INCIDENTS_FILE = "incident_engine/incidents.json"


def load_incidents() -> list:
    """Load all incidents from the JSON store."""
    if not os.path.exists(INCIDENTS_FILE):
        return []

    with open(INCIDENTS_FILE, "r") as f:
        return json.load(f)


def save_incidents(incidents: list) -> None:
    """Save the full incidents list back to the JSON store."""
    with open(INCIDENTS_FILE, "w") as f:
        json.dump(incidents, f, indent=2)


def generate_incident_id(incidents: list) -> str:
    """Generate the next sequential MET-INC-XXXXX ID."""
    next_number = len(incidents) + 1
    return f"MET-INC-{next_number:05d}"


def create_incident(
    dataset: str,
    incident_type: str,
    severity: str,
    expected: float,
    actual: float,
    deviation: float,
    root_cause: str = "Not yet determined",
    confidence: float = 0.0,
) -> dict:
    """Create a new incident and persist it."""
    incidents = load_incidents()

    incident = {
        "incident_id": generate_incident_id(incidents),
        "dataset": dataset,
        "type": incident_type,
        "severity": severity,
        "expected": expected,
        "actual": actual,
        "deviation": deviation,
        "root_cause": root_cause,
        "confidence": confidence,
        "status": "OPEN",
        "created_at": datetime.now().isoformat(),
        "acknowledged_at": None,
        "resolved_at": None,
    }

    incidents.append(incident)
    save_incidents(incidents)

    return incident


def acknowledge_incident(incident_id: str) -> dict:
    """Mark an incident as ACKNOWLEDGED."""
    incidents = load_incidents()

    for incident in incidents:
        if incident["incident_id"] == incident_id:
            incident["status"] = "ACKNOWLEDGED"
            incident["acknowledged_at"] = datetime.now().isoformat()
            save_incidents(incidents)
            return incident

    return {"error": f"Incident {incident_id} not found"}


def resolve_incident(incident_id: str) -> dict:
    """Mark an incident as RESOLVED."""
    incidents = load_incidents()

    for incident in incidents:
        if incident["incident_id"] == incident_id:
            incident["status"] = "RESOLVED"
            incident["resolved_at"] = datetime.now().isoformat()
            save_incidents(incidents)
            return incident

    return {"error": f"Incident {incident_id} not found"}


if __name__ == "__main__":
    from severity import calculate_severity

    print("=== CREATING INCIDENT (matching plan's example scenario) ===")
    deviation = -71.67
    severity = calculate_severity(deviation)

    incident = create_incident(
        dataset="orders",
        incident_type="VOLUME_ANOMALY",
        severity=severity,
        expected=1200000,
        actual=340000,
        deviation=deviation,
    )
    print(json.dumps(incident, indent=2))

    print("\n=== ACKNOWLEDGING INCIDENT ===")
    acknowledged = acknowledge_incident(incident["incident_id"])
    print(f"Status: {acknowledged['status']}, acknowledged_at: {acknowledged['acknowledged_at']}")

    print("\n=== RESOLVING INCIDENT ===")
    resolved = resolve_incident(incident["incident_id"])
    print(f"Status: {resolved['status']}, resolved_at: {resolved['resolved_at']}")
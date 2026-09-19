"""
Meteor - Incident Engine Unit Tests
Tests severity calculation and root cause pattern matching -
pure logic, no database dependency.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "incident_engine"))

from incident_engine.severity import calculate_severity
from incident_engine.root_cause import analyze_root_cause


def test_severity_critical_threshold():
    assert calculate_severity(-71.67) == "CRITICAL"
    assert calculate_severity(60.0) == "CRITICAL"


def test_severity_high_threshold():
    assert calculate_severity(-30.0) == "HIGH"


def test_severity_medium_threshold():
    assert calculate_severity(-12.5) == "MEDIUM"


def test_severity_low_threshold():
    assert calculate_severity(-5.0) == "LOW"
    assert calculate_severity(3.2) == "LOW"


def test_root_cause_volume_and_freshness():
    result = analyze_root_cause(volume_anomaly=True, freshness_failure=True)
    assert result["root_cause"] == "Upstream ingestion failure"
    assert result["confidence"] == 92


def test_root_cause_volume_only():
    result = analyze_root_cause(volume_anomaly=True)
    assert "Partial ingestion failure" in result["root_cause"]


def test_root_cause_schema_drift_only():
    result = analyze_root_cause(schema_drift=True)
    assert result["root_cause"] == "Upstream schema change"


def test_root_cause_no_symptoms_returns_unknown():
    result = analyze_root_cause()
    assert "Unknown" in result["root_cause"]
    assert result["confidence"] < 50
"""
Meteor - API Integration Tests
Tests real FastAPI endpoints end-to-end against the live database.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_get_datasets_returns_list():
    response = client.get("/datasets")
    assert response.status_code == 200
    assert "datasets" in response.json()
    assert len(response.json()["datasets"]) > 0


def test_get_dataset_by_id_valid():
    response = client.get("/datasets/1")
    assert response.status_code == 200
    assert response.json()["name"] == "orders"


def test_get_dataset_by_id_not_found():
    response = client.get("/datasets/99999")
    assert response.status_code == 404


def test_get_dataset_quality():
    response = client.get("/datasets/1/quality")
    assert response.status_code == 200
    data = response.json()
    assert "quality_score" in data
    assert "overall_quality_score" in data["quality_score"]


def test_get_dataset_schema():
    response = client.get("/datasets/1/schema")
    assert response.status_code == 200
    assert "schema_check" in response.json()


def test_get_dataset_anomalies():
    response = client.get("/datasets/1/anomalies")
    assert response.status_code == 200


def test_list_incidents():
    response = client.get("/incidents")
    assert response.status_code == 200
    assert "incidents" in response.json()


def test_get_incident_not_found():
    response = client.get("/incidents/MET-INC-99999")
    assert response.status_code == 404
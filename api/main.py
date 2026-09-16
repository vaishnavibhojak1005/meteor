"""
Meteor - FastAPI Backend
Exposes Meteor's data quality and incident data via a REST API.
"""

from fastapi import FastAPI

app = FastAPI(title="Meteor API", version="0.1.0")


@app.get("/health")
def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "service": "Meteor API"}
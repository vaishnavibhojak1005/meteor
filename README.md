# Meteor

AWS-Native Data Observability, Data Quality, Anomaly Detection & Intelligent Incident Management Platform.
# Meteor

**AWS-Native Data Observability, Data Quality, Anomaly Detection & Intelligent Incident Management Platform**

An educational, open-source implementation demonstrating how a modern data observability platform can be engineered from the ground up — built end-to-end by hand, one phase at a time, from synthetic data generation through a live full-stack application backed by real cloud infrastructure.

## Problem

Data pipelines fail silently. A dropped file, a schema change, or a stalled job often goes unnoticed until it causes downstream damage. Meteor detects these failures automatically, explains what likely caused them, shows what's affected, and alerts the right people — closing the loop from "something broke" to "here's what happened and what to do about it."

## What Meteor Does

- Profiles and validates datasets (completeness, duplicates, validity, freshness, schema drift)
- Detects anomalies using statistical methods (z-score, deviation) and machine learning (Isolation Forest)
- Creates structured incidents with automatic severity classification and deterministic root-cause analysis
- Tracks dataset lineage and computes downstream blast-radius when something fails
- Alerts engineers via email (AWS SNS) with full incident context
- Visualizes everything through a live React dashboard
- Runs real, verified AWS infrastructure: S3, Lambda, EventBridge, Kinesis, Athena, SNS, IAM, Terraform

## Architecture
CSV / Streaming Events
↓
Ingestion (S3, Kinesis)
↓
Processing (PySpark: validate → clean → dedupe → quarantine → Parquet)
↓
Quality Engine + Anomaly Engine (statistical + ML)
↓
Incident Engine (severity, root cause, lifecycle)
↓
PostgreSQL ←→ FastAPI ←→ React Dashboard
↓
SNS Alerts

## Technology Stack

**Backend:** Python, FastAPI, PostgreSQL (Docker), pandas, scikit-learn, PySpark
**Frontend:** React, Vite, React Router, Axios
**Cloud (AWS):** S3, Lambda, EventBridge, Kinesis, Athena, Glue (Data Catalog), SNS, IAM, Terraform
**Testing:** pytest (32 automated tests — unit, integration, API, data quality, anomaly detection)

## Local Setup

```bash
# Clone and enter the repo
git clone https://github.com/vaishnavibhojak1005/meteor.git
cd meteor

# Python environment
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Environment variables
cp .env.example .env   # fill in real DB credentials

# Database
docker run --name meteor-postgres -e POSTGRES_USER=meteor_admin \
  -e POSTGRES_PASSWORD=<your_password> -e POSTGRES_DB=meteor_db \
  -p 5432:5432 -d postgres:16
docker exec -i meteor-postgres psql -U meteor_admin -d meteor_db < quality_engine/schema.sql

# Generate data
py scripts/generate_data.py
py scripts/corrupt_data.py

# Run the API
uvicorn api.main:app --reload

# Run the frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## Testing

```bash
py -m pytest tests/ -v
```

32 tests covering data quality checks, statistical anomaly detection, incident lifecycle logic, and full API integration — all passing.

## AWS Architecture

Full details, including a documented and thoroughly-investigated Glue ETL job restriction (an AWS account-level issue, not a code defect — reported to AWS Support and confirmed via testing across 3 regions, both CLI and console, and both Glue job types), are in [`docs/aws.md`](docs/aws.md).

## Documentation

- [`docs/aws.md`](docs/aws.md) — AWS resources, configuration, and known issues
- [`docs/security.md`](docs/security.md) — credential handling and a real security fix made mid-project
- [`docs/failure-injection.md`](docs/failure-injection.md) — evidence-based test results for every failure scenario
- [`meteor-interview-prep.md`](meteor-interview-prep.md) — phase-by-phase rationale for interview preparation

## Limitations & Honest Notes

- AWS Glue ETL job creation is currently blocked by an account-level AWS restriction unrelated to this project's code (see docs/aws.md). All supporting infrastructure (IAM role, script, S3 upload) is complete and ready.
- ML-based anomaly detection (Isolation Forest) is implemented but flagged as low-confidence until more historical data accumulates — a deliberate, honest design choice rather than a hidden limitation.
- IAM currently uses broad `AdministratorAccess` for the learning/development stage; least-privilege policies are a documented, tracked gap (see docs/security.md).
- Scale has been tested at the 1,000-row synthetic dataset level, not benchmarked at production data volumes.

## License

MIT
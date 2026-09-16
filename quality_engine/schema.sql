-- Meteor Database Schema
-- Core tables for tracking datasets, pipelines, quality, and incidents

CREATE TABLE IF NOT EXISTS datasets (
    dataset_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS pipelines (
    pipeline_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    dataset_id INTEGER REFERENCES datasets(dataset_id),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS pipeline_runs (
    run_id SERIAL PRIMARY KEY,
    pipeline_id INTEGER REFERENCES pipelines(pipeline_id),
    record_count INTEGER,
    null_percentage NUMERIC(5,2),
    duplicate_percentage NUMERIC(5,2),
    mean_order_amount NUMERIC(10,2),
    std_order_amount NUMERIC(10,2),
    freshness_delay_hours NUMERIC(10,2),
    processing_time_seconds NUMERIC(10,4),
    schema_change_count INTEGER,
    run_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS quality_results (
    result_id SERIAL PRIMARY KEY,
    run_id INTEGER REFERENCES pipeline_runs(run_id),
    check_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    details JSONB,
    checked_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS incidents (
    incident_id VARCHAR(20) PRIMARY KEY,
    dataset_id INTEGER REFERENCES datasets(dataset_id),
    incident_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    expected NUMERIC(15,2),
    actual NUMERIC(15,2),
    deviation NUMERIC(6,2),
    root_cause TEXT,
    confidence NUMERIC(5,2),
    status VARCHAR(20) NOT NULL DEFAULT 'OPEN',
    created_at TIMESTAMP DEFAULT NOW(),
    acknowledged_at TIMESTAMP,
    resolved_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS lineage (
    lineage_id SERIAL PRIMARY KEY,
    upstream_dataset_id INTEGER REFERENCES datasets(dataset_id),
    downstream_dataset_id INTEGER REFERENCES datasets(dataset_id),
    created_at TIMESTAMP DEFAULT NOW()
);
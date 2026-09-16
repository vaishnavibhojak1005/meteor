"""
Meteor - ML-Based Anomaly Detection
Uses IsolationForest on dataset-level (per-run) features to detect
anomalous pipeline runs, complementing statistical detection.

NOTE: With very few historical runs, this model has limited
statistical power. It becomes meaningful once dozens of real
pipeline runs have been recorded.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from sklearn.ensemble import IsolationForest

from quality_engine.baseline import load_history

FEATURE_COLUMNS = [
    "record_count",
    "null_percentage",
    "duplicate_percentage",
    "mean_order_amount",
    "std_order_amount",
    "freshness_delay_hours",
]


def train_isolation_forest(history_df: pd.DataFrame) -> IsolationForest:
    """Train an IsolationForest model on historical run features."""
    features = history_df[FEATURE_COLUMNS].fillna(0)
    model = IsolationForest(contamination=0.2, random_state=42)
    model.fit(features)
    return model


MIN_RELIABLE_SAMPLES = 20


def detect_ml_anomaly(model: IsolationForest, current_metrics: dict, training_sample_size: int) -> dict:
    """Score a single run's metrics using the trained model."""
    row = pd.DataFrame([{col: current_metrics.get(col, 0) for col in FEATURE_COLUMNS}])

    prediction = model.predict(row)[0]
    anomaly_score = round(model.decision_function(row)[0], 4)

    confidence = "LOW - insufficient training data" if training_sample_size < MIN_RELIABLE_SAMPLES else "NORMAL"

    return {
        "prediction": "ANOMALY" if prediction == -1 else "NORMAL",
        "anomaly_score": anomaly_score,
        "confidence": confidence,
        "training_sample_size": training_sample_size,
    }


if __name__ == "__main__":
    history = load_history("orders")
    print(f"Training on {len(history)} historical runs.")

    if len(history) < 5:
        print("WARNING: Very few historical runs available. Results are not statistically meaningful yet.")

    model = train_isolation_forest(history)

    print("\n=== TESTING: NORMAL-LOOKING RUN ===")
    normal_run = {
        "record_count": 1010,
        "null_percentage": 0.0,
        "duplicate_percentage": 0.0,
        "mean_order_amount": 2500.0,
        "std_order_amount": 1400.0,
        "freshness_delay_hours": 3.0,
    }
    print(detect_ml_anomaly(model, normal_run, training_sample_size=len(history)))

    print("\n=== TESTING: SEVERE VOLUME DROP RUN ===")
    anomaly_run = {
        "record_count": 340,
        "null_percentage": 35.0,
        "duplicate_percentage": 10.0,
        "mean_order_amount": 2500.0,
        "std_order_amount": 1400.0,
        "freshness_delay_hours": 3.0,
    }
    print(detect_ml_anomaly(model, anomaly_run, training_sample_size=len(history)))
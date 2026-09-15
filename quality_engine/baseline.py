"""
Meteor - Historical Baseline Tracker
Records dataset metrics over time and computes basic statistics
(mean, median, std, percentiles, rolling average) needed for
anomaly detection.
"""

import os
import time
from datetime import datetime

import pandas as pd

HISTORY_FILE = "quality_engine/history.csv"

HISTORY_COLUMNS = [
    "timestamp",
    "dataset",
    "record_count",
    "null_percentage",
    "duplicate_percentage",
    "mean_order_amount",
    "std_order_amount",
    "freshness_delay_hours",
    "processing_time_seconds",
    "schema_change_count",
]


def record_run(
    dataset_name: str,
    record_count: int,
    null_percentage: float,
    duplicate_percentage: float,
    mean_order_amount: float,
    std_order_amount: float,
    freshness_delay_hours: float,
    processing_time_seconds: float,
    schema_change_count: int,
) -> None:
    """Append a single run's metrics to the history log."""
    row = {
        "timestamp": datetime.now().isoformat(),
        "dataset": dataset_name,
        "record_count": record_count,
        "null_percentage": null_percentage,
        "duplicate_percentage": duplicate_percentage,
        "mean_order_amount": mean_order_amount,
        "std_order_amount": std_order_amount,
        "freshness_delay_hours": freshness_delay_hours,
        "processing_time_seconds": processing_time_seconds,
        "schema_change_count": schema_change_count,
    }

    file_exists = os.path.exists(HISTORY_FILE)
    df_row = pd.DataFrame([row])
    df_row.to_csv(HISTORY_FILE, mode="a", header=not file_exists, index=False)


def load_history(dataset_name: str = None) -> pd.DataFrame:
    """Load the full history log, optionally filtered to one dataset."""
    if not os.path.exists(HISTORY_FILE):
        return pd.DataFrame(columns=HISTORY_COLUMNS)

    df = pd.read_csv(HISTORY_FILE)
    if dataset_name:
        df = df[df["dataset"] == dataset_name]
    return df


def compute_baseline_stats(history_df: pd.DataFrame, column: str) -> dict:
    """Compute mean, median, std, min, max, and percentiles for a metric column."""
    series = history_df[column].dropna()

    if series.empty:
        return {"status": "NO_HISTORY"}

    return {
        "mean": round(series.mean(), 2),
        "median": round(series.median(), 2),
        "std": round(series.std(), 2) if len(series) > 1 else 0.0,
        "min": round(series.min(), 2),
        "max": round(series.max(), 2),
        "p25": round(series.quantile(0.25), 2),
        "p75": round(series.quantile(0.75), 2),
        "rolling_avg_last_5": round(series.tail(5).mean(), 2),
        "sample_size": len(series),
    }


if __name__ == "__main__":
    # Simulate recording a few runs for the 'orders' dataset
    df = pd.read_csv("data/orders.csv")

    start = time.time()
    record_count = len(df)
    null_percentage = round(df.isnull().mean().mean() * 100, 2)
    duplicate_percentage = round((1 - df["order_id"].nunique() / len(df)) * 100, 2)
    mean_amount = round(df["order_amount"].mean(), 2)
    std_amount = round(df["order_amount"].std(), 2)
    processing_time = round(time.time() - start, 4)

    record_run(
        dataset_name="orders",
        record_count=record_count,
        null_percentage=null_percentage,
        duplicate_percentage=duplicate_percentage,
        mean_order_amount=mean_amount,
        std_order_amount=std_amount,
        freshness_delay_hours=3.0,
        processing_time_seconds=processing_time,
        schema_change_count=0,
    )

    print(f"Recorded run for 'orders': {record_count} records, mean_amount={mean_amount}")

    history = load_history("orders")
    print(f"\nTotal historical runs for 'orders': {len(history)}")

    stats = compute_baseline_stats(history, "record_count")
    print(f"\nBaseline stats for record_count: {stats}")
    
"""
Meteor - Corrupted Data Generator
Creates intentionally broken versions of the orders dataset
to test Meteor's data quality and anomaly detection.
"""

import random

import pandas as pd

SOURCE_FILE = "data/orders.csv"


def load_clean_orders() -> pd.DataFrame:
    """Load the clean synthetic orders dataset."""
    return pd.read_csv(SOURCE_FILE)


def inject_null_anomaly(df: pd.DataFrame, null_fraction: float = 0.35) -> pd.DataFrame:
    """Randomly null out a fraction of values in 'payment_status' and 'city'."""
    corrupted = df.copy()
    num_rows = len(corrupted)
    num_nulls = int(num_rows * null_fraction)

    null_indices = random.sample(range(num_rows), num_nulls)
    corrupted.loc[null_indices, "payment_status"] = None

    null_indices_city = random.sample(range(num_rows), num_nulls)
    corrupted.loc[null_indices_city, "city"] = None

    return corrupted


def inject_duplicate_anomaly(df: pd.DataFrame, duplicate_fraction: float = 0.10) -> pd.DataFrame:
    """Duplicate a fraction of existing rows, creating repeated order_ids."""
    corrupted = df.copy()
    num_duplicates = int(len(df) * duplicate_fraction)

    duplicate_rows = df.sample(n=num_duplicates, replace=False)
    corrupted = pd.concat([corrupted, duplicate_rows], ignore_index=True)

    return corrupted


if __name__ == "__main__":
    clean_orders = load_clean_orders()
    print(f"Loaded {len(clean_orders)} clean rows from {SOURCE_FILE}")

    null_anomaly_df = inject_null_anomaly(clean_orders)
    null_anomaly_df.to_csv("data/null_anomaly_orders.csv", index=False)
    print(f"Generated {len(null_anomaly_df)} rows -> data/null_anomaly_orders.csv")

    duplicate_anomaly_df = inject_duplicate_anomaly(clean_orders)
    duplicate_anomaly_df.to_csv("data/duplicate_anomaly_orders.csv", index=False)
    print(f"Generated {len(duplicate_anomaly_df)} rows -> data/duplicate_anomaly_orders.csv")
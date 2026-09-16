"""
Meteor - Data Profiler

Inspects a dataset and reports:
- row count
- column count
- column names
- data types
- null counts
- unique value counts
- numeric statistics
- timestamp information
"""

import pandas as pd


NUMERIC_DTYPES = [
    "int64",
    "float64",
]


def profile_structure(df: pd.DataFrame) -> dict:
    """Return basic structural facts about a DataFrame."""

    return {
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "column_names": list(df.columns),
        "data_types": {
            col: str(dtype)
            for col, dtype in df.dtypes.items()
        },
    }


def profile_nulls(df: pd.DataFrame) -> dict:
    """Return null count and null percentage per column."""

    null_counts = df.isnull().sum()
    total_rows = len(df)

    return {
        col: {
            "null_count": int(null_counts[col]),
            "null_percentage": float(
                round(
                    (null_counts[col] / total_rows) * 100,
                    2,
                )
            )
            if total_rows
            else 0.0,
        }
        for col in df.columns
    }


def profile_unique_values(df: pd.DataFrame) -> dict:
    """Return the number of unique values per column."""

    return {
        col: int(df[col].nunique())
        for col in df.columns
    }


def profile_numeric_stats(df: pd.DataFrame) -> dict:
    """Return mean, std, min, max, and percentiles for numeric columns."""

    stats = {}

    for col in df.columns:

        if str(df[col].dtype) in NUMERIC_DTYPES:

            series = df[col].dropna()

            if series.empty:
                continue

            stats[col] = {
                "mean": float(
                    round(series.mean(), 2)
                ),
                "std": float(
                    round(series.std(), 2)
                ),
                "min": float(
                    round(series.min(), 2)
                ),
                "max": float(
                    round(series.max(), 2)
                ),
                "p25": float(
                    round(series.quantile(0.25), 2)
                ),
                "p50": float(
                    round(series.quantile(0.50), 2)
                ),
                "p75": float(
                    round(series.quantile(0.75), 2)
                ),
            }

    return stats


def profile_timestamp_columns(
    df: pd.DataFrame,
    timestamp_columns: list[str],
) -> dict:
    """Return earliest, latest, and span for specified timestamp columns."""

    info = {}

    for col in timestamp_columns:

        if col not in df.columns:
            continue

        parsed = pd.to_datetime(
            df[col],
            errors="coerce",
        ).dropna()

        if parsed.empty:
            continue

        earliest = parsed.min()
        latest = parsed.max()

        info[col] = {
            "earliest": str(earliest),
            "latest": str(latest),
            "span_days": int(
                (latest - earliest).days
            ),
        }

    return info


if __name__ == "__main__":

    df = pd.read_csv("data/orders.csv")

    structure = profile_structure(df)
    nulls = profile_nulls(df)
    uniques = profile_unique_values(df)
    numeric_stats = profile_numeric_stats(df)

    timestamp_info = profile_timestamp_columns(
        df,
        timestamp_columns=["order_date"],
    )

    print("=== METEOR PROFILER ===")

    print(f"Row count:    {structure['row_count']}")
    print(f"Column count: {structure['column_count']}")
    print(f"Columns:      {structure['column_names']}")

    print("\nData types:")

    for col, dtype in structure["data_types"].items():
        print(f"  {col}: {dtype}")

    print("\nNulls:")

    for col, info in nulls.items():
        print(
            f"  {col}: "
            f"{info['null_count']} nulls "
            f"({info['null_percentage']}%)"
        )

    print("\nUnique values:")

    for col, count in uniques.items():
        print(
            f"  {col}: {count} unique"
        )

    print("\nNumeric statistics:")

    for col, stats in numeric_stats.items():
        print(
            f"  {col}: {stats}"
        )

    print("\nTimestamp info:")

    for col, info in timestamp_info.items():
        print(
            f"  {col}: "
            f"earliest={info['earliest']}, "
            f"latest={info['latest']}, "
            f"span_days={info['span_days']}"
        )
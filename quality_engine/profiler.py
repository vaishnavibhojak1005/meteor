"""
Meteor - Data Profiler
Inspects a dataset and reports structural facts: row count,
column count, column names, data types, null counts, and
unique value counts.
"""

import pandas as pd


def profile_structure(df: pd.DataFrame) -> dict:
    """Return basic structural facts about a DataFrame."""
    return {
        "row_count": len(df),
        "column_count": len(df.columns),
        "column_names": list(df.columns),
        "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
    }


def profile_nulls(df: pd.DataFrame) -> dict:
    """Return null count and null percentage per column."""
    null_counts = df.isnull().sum()
    total_rows = len(df)

    return {
        col: {
            "null_count": int(null_counts[col]),
            "null_percentage": round((null_counts[col] / total_rows) * 100, 2) if total_rows else 0.0,
        }
        for col in df.columns
    }


def profile_unique_values(df: pd.DataFrame) -> dict:
    """Return the number of unique values per column."""
    return {col: int(df[col].nunique()) for col in df.columns}


if __name__ == "__main__":
    df = pd.read_csv("data/orders.csv")

    structure = profile_structure(df)
    nulls = profile_nulls(df)
    uniques = profile_unique_values(df)

    print("=== METEOR PROFILER ===")
    print(f"Row count:    {structure['row_count']}")
    print(f"Column count: {structure['column_count']}")
    print(f"Columns:      {structure['column_names']}")

    print("\nData types:")
    for col, dtype in structure["data_types"].items():
        print(f"  {col}: {dtype}")

    print("\nNulls:")
    for col, info in nulls.items():
        print(f"  {col}: {info['null_count']} nulls ({info['null_percentage']}%)")

    print("\nUnique values:")
    for col, count in uniques.items():
        print(f"  {col}: {count} unique")
"""
Meteor - Lineage Manager
Tracks dataset dependencies and computes downstream impact
when a dataset fails.
"""

import psycopg2
import psycopg2.extras
import os

from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def get_direct_downstream(dataset_id: int) -> list:
    """Get datasets that directly depend on the given dataset."""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(
        """
        SELECT d.dataset_id, d.name
        FROM lineage l
        JOIN datasets d ON l.downstream_dataset_id = d.dataset_id
        WHERE l.upstream_dataset_id = %s;
        """,
        (dataset_id,),
    )
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result


def get_full_downstream_impact(dataset_id: int) -> list:
    """Get ALL downstream dependents (direct and indirect) using BFS."""
    visited = []
    visited_ids = set()
    queue = [dataset_id]

    while queue:
        current_id = queue.pop(0)
        direct_children = get_direct_downstream(current_id)

        for child in direct_children:
            if child["dataset_id"] not in visited_ids:
                visited.append(child)
                visited_ids.add(child["dataset_id"])
                queue.append(child["dataset_id"])

    return visited


def get_dataset_name(dataset_id: int) -> str:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM datasets WHERE dataset_id = %s;", (dataset_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row[0] if row else "UNKNOWN"


if __name__ == "__main__":
    print("=== TESTING: What depends on orders_raw (id=2)? ===")
    impact = get_full_downstream_impact(2)

    print(f"\nIf 'orders_raw' fails, affected downstream datasets:")
    for dataset in impact:
        print(f"  - {dataset['name']}")

    print(f"\nTotal affected: {len(impact)}")
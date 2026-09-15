"""
Meteor - Synthetic Data Generator
Generates a synthetic 'orders' dataset for testing data quality
and anomaly detection.
"""

import random
from datetime import datetime, timedelta

import pandas as pd
from faker import Faker

fake = Faker()

NUM_ROWS = 1000

PAYMENT_STATUSES = ["SUCCESS", "FAILED", "PENDING"]
CITIES = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Pune", "Hyderabad", "Kolkata"]


def generate_orders(num_rows: int) -> pd.DataFrame:
    """Generate a synthetic orders dataset."""
    rows = []

    for order_id in range(1, num_rows + 1):
        customer_id = random.randint(1, 300)
        product_id = random.randint(1, 100)
        order_amount = round(random.uniform(50, 5000), 2)
        order_date = fake.date_time_between(start_date="-90d", end_date="now")
        payment_status = random.choice(PAYMENT_STATUSES)
        city = random.choice(CITIES)

        rows.append({
            "order_id": order_id,
            "customer_id": customer_id,
            "product_id": product_id,
            "order_amount": order_amount,
            "order_date": order_date,
            "payment_status": payment_status,
            "city": city,
        })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = generate_orders(NUM_ROWS)
    df.to_csv("data/orders.csv", index=False)
    print(f"Generated {len(df)} rows -> data/orders.csv")
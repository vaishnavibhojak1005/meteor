"""
Meteor - Synthetic Data Generator
Generates synthetic 'orders', 'payments', 'inventory', and 'shipments'
datasets for testing data quality and anomaly detection.
"""

import random
from datetime import timedelta

import pandas as pd
from faker import Faker

fake = Faker()

NUM_ROWS = 1000
NUM_PRODUCTS = 100
NUM_WAREHOUSES = 5

PAYMENT_STATUSES = ["SUCCESS", "FAILED", "PENDING"]
CITIES = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Pune", "Hyderabad", "Kolkata"]
PAYMENT_METHODS = ["CREDIT_CARD", "DEBIT_CARD", "UPI", "NET_BANKING", "COD"]
CARRIERS = ["BlueDart", "Delhivery", "DTDC", "Ekart", "IndiaPost"]
SHIPMENT_STATUSES = ["PENDING", "IN_TRANSIT", "DELIVERED", "RETURNED"]


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


def generate_payments(orders_df: pd.DataFrame) -> pd.DataFrame:
    """Generate a synthetic payments dataset linked to orders."""
    rows = []

    for payment_id, order_row in enumerate(orders_df.itertuples(), start=1):
        order_id = order_row.order_id
        customer_id = order_row.customer_id
        amount = order_row.order_amount
        payment_method = random.choice(PAYMENT_METHODS)
        payment_status = random.choice(PAYMENT_STATUSES)
        payment_timestamp = order_row.order_date + timedelta(minutes=random.randint(1, 30))

        rows.append({
            "payment_id": payment_id,
            "order_id": order_id,
            "customer_id": customer_id,
            "amount": amount,
            "payment_method": payment_method,
            "payment_status": payment_status,
            "payment_timestamp": payment_timestamp,
        })

    return pd.DataFrame(rows)


def generate_inventory(num_products: int, num_warehouses: int) -> pd.DataFrame:
    """Generate a synthetic inventory snapshot: one row per product per warehouse."""
    rows = []

    for product_id in range(1, num_products + 1):
        for warehouse_id in range(1, num_warehouses + 1):
            stock_quantity = random.randint(0, 500)
            reorder_level = random.randint(20, 100)
            last_updated = fake.date_time_between(start_date="-7d", end_date="now")

            rows.append({
                "product_id": product_id,
                "warehouse_id": warehouse_id,
                "stock_quantity": stock_quantity,
                "reorder_level": reorder_level,
                "last_updated": last_updated,
            })

    return pd.DataFrame(rows)


def generate_shipments(orders_df: pd.DataFrame, num_warehouses: int) -> pd.DataFrame:
    """Generate a synthetic shipments dataset linked to orders."""
    rows = []

    for shipment_id, order_row in enumerate(orders_df.itertuples(), start=1):
        order_id = order_row.order_id
        warehouse_id = random.randint(1, num_warehouses)
        carrier = random.choice(CARRIERS)
        shipment_status = random.choice(SHIPMENT_STATUSES)
        shipment_date = order_row.order_date + timedelta(days=random.randint(0, 2))

        if shipment_status == "DELIVERED":
            delivery_date = shipment_date + timedelta(days=random.randint(1, 7))
        else:
            delivery_date = None

        rows.append({
            "shipment_id": shipment_id,
            "order_id": order_id,
            "warehouse_id": warehouse_id,
            "carrier": carrier,
            "shipment_status": shipment_status,
            "shipment_date": shipment_date,
            "delivery_date": delivery_date,
        })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    orders_df = generate_orders(NUM_ROWS)
    orders_df.to_csv("data/orders.csv", index=False)
    print(f"Generated {len(orders_df)} rows -> data/orders.csv")

    payments_df = generate_payments(orders_df)
    payments_df.to_csv("data/payments.csv", index=False)
    print(f"Generated {len(payments_df)} rows -> data/payments.csv")

    inventory_df = generate_inventory(NUM_PRODUCTS, NUM_WAREHOUSES)
    inventory_df.to_csv("data/inventory.csv", index=False)
    print(f"Generated {len(inventory_df)} rows -> data/inventory.csv")

    shipments_df = generate_shipments(orders_df, NUM_WAREHOUSES)
    shipments_df.to_csv("data/shipments.csv", index=False)
    print(f"Generated {len(shipments_df)} rows -> data/shipments.csv")
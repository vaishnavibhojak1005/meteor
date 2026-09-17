"""
Meteor - Kinesis Producer
Sends simulated order events to a real AWS Kinesis Data Stream.
"""

import json
import random
import time
import uuid
from datetime import datetime

import boto3

STREAM_NAME = "meteor-orders-stream"
CITIES = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Pune"]

kinesis = boto3.client("kinesis", region_name="us-east-1")


def generate_event() -> dict:
    """Generate a single simulated order event."""
    return {
        "event_id": str(uuid.uuid4())[:8],
        "order_id": random.randint(1000, 9999),
        "amount": round(random.uniform(50, 5000), 2),
        "city": random.choice(CITIES),
        "timestamp": datetime.now().isoformat(),
    }


def send_event(event: dict):
    """Send one event to Kinesis, partitioned by city."""
    response = kinesis.put_record(
        StreamName=STREAM_NAME,
        Data=json.dumps(event),
        PartitionKey=event["city"],
    )
    print(f"Sent: {event} -> Shard: {response['ShardId']}")


if __name__ == "__main__":
    print("Sending 10 events to Kinesis...")
    for i in range(10):
        event = generate_event()
        send_event(event)
        time.sleep(0.5)
    print("Done sending.")
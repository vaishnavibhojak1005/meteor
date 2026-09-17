"""
Meteor - Local Streaming Simulator (Producer)
Simulates a stream of order events, writing them to a local
'stream' file that a consumer can read from — mimicking the
producer/consumer pattern before using real Kinesis.
"""

import json
import random
import time
import uuid
from datetime import datetime

STREAM_FILE = "streaming/local_stream.jsonl"

CITIES = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Pune"]


def generate_event() -> dict:
    """Generate a single simulated order event."""
    return {
        "event_id": str(uuid.uuid4())[:8],
        "order_id": random.randint(1000, 9999),
        "amount": round(random.uniform(50, 5000), 2),
        "city": random.choice(CITIES),
        "timestamp": datetime.now().isoformat(),
    }


def produce_events(num_events: int, delay_seconds: float = 1.0):
    """Generate events one at a time, appending each to the stream file."""
    with open(STREAM_FILE, "a") as f:
        for i in range(num_events):
            event = generate_event()
            f.write(json.dumps(event) + "\n")
            f.flush()
            print(f"Produced: {event}")
            time.sleep(delay_seconds)


if __name__ == "__main__":
    print("Starting producer - generating 10 events, 1 per second...")
    produce_events(num_events=10, delay_seconds=1.0)
    print("Done producing.")
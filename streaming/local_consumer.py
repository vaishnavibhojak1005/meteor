"""
Meteor - Local Streaming Simulator (Consumer)
Reads events from the local stream file and processes them,
flagging amount anomalies, duplicate events, and abnormal volume.
"""

import json
from collections import Counter
from datetime import datetime

STREAM_FILE = "streaming/local_stream.jsonl"

AMOUNT_ANOMALY_THRESHOLD = 4000
NORMAL_EVENTS_PER_MINUTE = 100
VOLUME_SPIKE_MULTIPLIER = 5


def consume_events():
    """Read and process every event currently in the stream file."""
    events = []

    with open(STREAM_FILE, "r") as f:
        for line in f:
            events.append(json.loads(line))

    processed_count = len(events)
    amount_anomalies = 0
    seen_event_ids = set()
    duplicate_ids = []

    for event in events:
        if event["amount"] > AMOUNT_ANOMALY_THRESHOLD:
            amount_anomalies += 1
            print(f"AMOUNT ANOMALY: order {event['order_id']} amount={event['amount']}")

        if event["event_id"] in seen_event_ids:
            duplicate_ids.append(event["event_id"])
            print(f"DUPLICATE EVENT: {event['event_id']} (order {event['order_id']})")
        else:
            seen_event_ids.add(event["event_id"])

    volume_status = check_volume_anomaly(events)

    print(f"\n=== SUMMARY ===")
    print(f"Total events processed: {processed_count}")
    print(f"Amount anomalies: {amount_anomalies}")
    print(f"Duplicate events: {len(duplicate_ids)}")
    print(f"Volume status: {volume_status}")


def check_volume_anomaly(events: list) -> str:
    """Estimate events-per-minute based on timestamp span and compare to normal."""
    if len(events) < 2:
        return "NOT_ENOUGH_DATA"

    timestamps = [datetime.fromisoformat(e["timestamp"]) for e in events]
    span_seconds = (max(timestamps) - min(timestamps)).total_seconds()

    if span_seconds == 0:
        return "NOT_ENOUGH_DATA"

    events_per_minute = (len(events) / span_seconds) * 60

    if events_per_minute > NORMAL_EVENTS_PER_MINUTE * VOLUME_SPIKE_MULTIPLIER:
        return f"ANOMALY - {round(events_per_minute, 1)} events/min (expected ~{NORMAL_EVENTS_PER_MINUTE})"

    return f"NORMAL - {round(events_per_minute, 1)} events/min"


if __name__ == "__main__":
    consume_events()
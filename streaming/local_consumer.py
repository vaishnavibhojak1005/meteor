"""
Meteor - Local Streaming Simulator (Consumer)
Reads events from the local stream file and processes them,
flagging simple anomalies (e.g., unusually large amounts).
"""

import json

STREAM_FILE = "streaming/local_stream.jsonl"

AMOUNT_ANOMALY_THRESHOLD = 4000


def consume_events():
    """Read and process every event currently in the stream file."""
    processed_count = 0
    anomaly_count = 0

    with open(STREAM_FILE, "r") as f:
        for line in f:
            event = json.loads(line)
            processed_count += 1

            if event["amount"] > AMOUNT_ANOMALY_THRESHOLD:
                anomaly_count += 1
                print(f"ANOMALY: order {event['order_id']} amount={event['amount']} (event {event['event_id']})")
            else:
                print(f"OK: order {event['order_id']} amount={event['amount']}")

    print(f"\nProcessed {processed_count} events, {anomaly_count} anomalies detected.")


if __name__ == "__main__":
    consume_events()
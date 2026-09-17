"""
Meteor - Kinesis Consumer
Reads events from the AWS Kinesis Data Stream and checks for
amount anomalies.
"""

import json

import boto3

STREAM_NAME = "meteor-orders-stream"
AMOUNT_ANOMALY_THRESHOLD = 4000

kinesis = boto3.client("kinesis", region_name="us-east-1")


def get_shard_ids(stream_name: str) -> list:
    """Get all shard IDs for a stream."""
    response = kinesis.describe_stream_summary(StreamName=stream_name)
    stream_arn = response["StreamDescriptionSummary"]["StreamARN"]

    shards_response = kinesis.list_shards(StreamName=stream_name)
    return [shard["ShardId"] for shard in shards_response["Shards"]]


def consume_shard(stream_name: str, shard_id: str):
    """Read all currently available records from a single shard."""
    iterator_response = kinesis.get_shard_iterator(
        StreamName=stream_name,
        ShardId=shard_id,
        ShardIteratorType="TRIM_HORIZON",
    )
    shard_iterator = iterator_response["ShardIterator"]

    records_response = kinesis.get_records(ShardIterator=shard_iterator, Limit=100)
    records = records_response["Records"]

    processed_count = 0
    anomaly_count = 0

    for record in records:
        event = json.loads(record["Data"])
        processed_count += 1

        if event["amount"] > AMOUNT_ANOMALY_THRESHOLD:
            anomaly_count += 1
            print(f"ANOMALY: order {event['order_id']} amount={event['amount']}")
        else:
            print(f"OK: order {event['order_id']} amount={event['amount']}")

    return processed_count, anomaly_count


if __name__ == "__main__":
    shard_ids = get_shard_ids(STREAM_NAME)
    print(f"Found {len(shard_ids)} shard(s): {shard_ids}")

    total_processed = 0
    total_anomalies = 0

    for shard_id in shard_ids:
        processed, anomalies = consume_shard(STREAM_NAME, shard_id)
        total_processed += processed
        total_anomalies += anomalies

    print(f"\nTotal processed: {total_processed}, anomalies: {total_anomalies}")
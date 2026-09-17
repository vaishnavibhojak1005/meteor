"""
Meteor - S3 Trigger Test Lambda
Triggered automatically when a file is uploaded to S3.
Logs details about the uploaded file (no processing yet).
"""

import json


def handler(event, context):
    print("Received S3 event:")
    print(json.dumps(event))

    for record in event.get("Records", []):
        bucket_name = record["s3"]["bucket"]["name"]
        object_key = record["s3"]["object"]["key"]
        object_size = record["s3"]["object"]["size"]

        print(f"File uploaded: {object_key} ({object_size} bytes) in bucket {bucket_name}")

    return {
        "statusCode": 200,
        "body": "Event processed"
    }
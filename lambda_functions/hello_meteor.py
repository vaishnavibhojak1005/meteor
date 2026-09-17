"""
Meteor - Hello World Lambda
The simplest possible Lambda function, to confirm the deployment
pipeline works before building anything real.
"""

def handler(event, context):
    return {
        "statusCode": 200,
        "body": "Hello Meteor from Lambda!"
    }
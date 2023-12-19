import logging
import boto3
import json
import os

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
bucket = os.environ["BUCKET"]

s3 = boto3.client("s3")


def monitor(event, context):
    LOGGER.info(event)
    deets = event["detail"]
    query_id = deets["responseElements"]["queryExecutionId"]
    try:
        data = {
            "queryId": query_id,
            "roleId": deets["userIdentity"]["sessionContext"]["sessionIssuer"]["arn"],
        }
    except Exception as e:
        LOGGER.info(e)

    try:
        data = {
            "queryId": query_id,
            "roleId": deets["userIdentity"]["arn"],
        }
    except Exception as e:
        LOGGER.info(e)

    writeTos3 = s3.put_object(
        Bucket=bucket,
        Key=f"query_objects/{query_id}.json",
        Body=bytes(json.dumps(data).encode()),
    )

    return writeTos3

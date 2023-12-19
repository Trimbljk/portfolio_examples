import boto3
import os
import json
import logging
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

s3 = boto3.client("s3")

bucket = os.environ['BUCKET']
output_path = os.environ['OUTPUT_PATH']
LOGGER.info(f"BUCKET: {bucket}")
LOGGER.info(f"OUTPUT_PATH: {output_path}")

def write_events(event, context):

    LOGGER.info(f"EVENT: {event}")
    LOGGER.info(f"CONTEXT: {context}")

    filename = event['id']

    resp = s3.put_object(
        Bucket=bucket,
        Key=f"{output_path}/{filename}.json",
        Body=bytes(json.dumps(event).encode())
    )

    LOGGER.info(resp)

    return "200"


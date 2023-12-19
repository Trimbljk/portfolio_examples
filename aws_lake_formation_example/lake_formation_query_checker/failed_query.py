import logging
import boto3
import json
import os
from httplib2 import Http
import time

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
bucket = os.environ["BUCKET"]

s3 = boto3.client("s3")
athena = boto3.client("athena")


def monitor(event, context):
    """
    This function is triggered by objects loaded into s3 at the 'query_objects/'
    path in the lakeformation-metdata bucket.
    It checks for any failed queries in athena. The goal being to capture any issues regarding lakeformation
    """
    LOGGER.info(event)
    LOGGER.info(f"CONTEXT: {context}")
    LOGGER.info(f"LOG_STREAM_NAME: {context.log_stream_name}")

    key = json.loads(event["Records"][0]["Sns"]["Message"])["Records"][0]["s3"][
        "object"
    ]["key"]

    obj = s3.get_object(Bucket=bucket, Key=key)["Body"].read().decode()

    info = json.loads(obj)

    query_id = info["queryId"]
    role_id = info["roleId"]

    status = "UNKNOWN"

    # Sometimes the query takes a long time to finish so this while loops waits for it to fail or succeed
    while status not in ["FAILED", "SUCCEEDED"]:
        ath = athena.get_query_execution(QueryExecutionId=query_id)["QueryExecution"]
        status = ath["Status"]["State"]
        time.sleep(5)

    LOGGER.info(ath)

    if status == "FAILED":
        stateChange = ath["Status"]["StateChangeReason"]
        LOGGER.info(stateChange)
        if 'Lake Formation' not in stateChange:
            LOGGER.info("Not a Lake Formation error. Exiting...")
        else:
            LOGGER.info("Sending Error to chat...")
            chat(query=query_id, role=role_id, ctext=context.log_stream_name)
    else:
        LOGGER.info("No FAILURE detected... exiting")

    return "200"


def chat(query, role, ctext):
    """Hangouts Chat incoming webhook quickstart."""
    url = "enter a chat url"
    bot_message = {
        "cardsV2": [
            {
                "cardId": "unique-card-id",
                "card": {
                    "header": {
                        "title": "QUERY ERROR",
                        "subtitle": "There was an Athena query error.",
                    },
                    "sections": [
                        {
                            "header": "Event Details",
                            "collapsible": "false",
                            "widgets": [
                                {
                                    "decoratedText": {
                                        "text": f"ROLE_ID:  {role}",
                                    },
                                },
                                {
                                    "decoratedText": {
                                        "text": f"QUERY_ID:  {query}",
                                    }
                                },
                                {
                                    "decoratedText": {
                                        "text": f"ERROR_TYPE:  Insufficient Lake Formation Permissions",
                                    }
                                },
                                {
                                    "decoratedText": {
                                        "text": f"LOG_GROUP:  aws/lambda/FailedQueryLambda",
                                    }
                                },
                                {
                                    "decoratedText": {
                                        "text": f"LOG_STREAM_ID:  {ctext}",
                                    }
                                },
                            ],
                        },
                    ],
                },
            }
        ],
    }
    message_headers = {"Content-Type": "application/json; charset=UTF-8"}
    http_obj = Http()
    response = http_obj.request(
        uri=url,
        method="POST",
        headers=message_headers,
        body=json.dumps(bot_message),
    )
    return json.loads(response[1].decode())

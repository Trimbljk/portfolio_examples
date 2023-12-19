import boto3
import logging
import os
import json
import time
from lambdas.utils import DeleteActions
from lambdas import chat

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

glue = boto3.client("glue")
lf = boto3.client("lakeformation")
s3 = boto3.client("s3")

bucket = os.environ["BUCKET_NAME"]
table_action_path = os.environ["TABLE_ACTION"]
chat_url=os.environ["CHAT_URL"]

def update_event(event, context):
    if len(event['input']["UpdateTable"]) < 1:
        return "No tables to process"
    total_changes = 0
    for e in event['input']["UpdateTable"]:
        dbname = e["databaseName"]
        tbname = e["tableName"]
        LOGGER.info(f"DATABASE: {dbname}")
        LOGGER.info(f"TABLE: {tbname}")
        if e["tableType"] == "virtual_view":
            LOGGER.info("Updated VIEW. Skipping update...")
            deleteInfo = s3.delete_object(
                Bucket=bucket, Key=f"{table_action_path}/{e['eventId']}.json"
            )
            LOGGER.info(f"DELETE INFO: {deleteInfo}")
            continue

        table_s3_path = e["storageLocation"].split("//")[1]
        query_path = f"arn:aws:s3:::{table_s3_path}"
        if query_path[-1] == "/":
            pass
        else:
            query_path = query_path + "/"
        LOGGER.info(f"NEW PATH: {query_path}")

        actions = DeleteActions(database=dbname, table=tbname).run_queries(
            query_selector=["location"]
        )
        LOGGER.info(f"QUERIES: {actions.show()}")
        time.sleep(5)

        path_arn = actions.get_table_path()
        LOGGER.info(f"PATH TO UPDATE: {path_arn}")
        if path_arn == query_path:
            LOGGER.info("No change to table path")
        else:
            LOGGER.info("Attemping to replace registered resource...")
            try:
                resp = lf.deregister_resource(ResourceArn=path_arn)
                LOGGER.info(f"RESPONSE FROM DESRIGSTER: {resp}")
            except:
                LOGGER.info("There was an error removing the registered resource...")
            LOGGER.info("Attempting to register new resource...")
            try:
                resp = lf.register_resource(
                    ResourceArn=query_path, UseServiceLinkedRole=True
                )
                LOGGER.info(f"RESPONSE FROM NEW REGISTRATION: {resp}")
            except:
                LOGGER.info("There was an error registering the new resource path...")

        total_changes += 1

        # Send message to chat

        chat_resp = chat.messenger(
            event_type="UpdateTable",
            database=dbname,
            table=tbname,
            statelogs=event["execName"],
            stream=context.log_stream_name,
            chatUrl=chat_url
        )
        LOGGER.info(chat_resp)

    return total_changes

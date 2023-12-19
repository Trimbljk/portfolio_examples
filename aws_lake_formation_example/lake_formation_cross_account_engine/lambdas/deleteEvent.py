import boto3
import logging
import os
import json
import uuid
import time
from lambdas.utils import DeleteActions
from lambdas import chat

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

bucket = os.environ["BUCKET_NAME"]
type_path = os.environ["TYPE_PATH"]
saved_state_path = os.environ["SAVED_STATE"]
table_action_path = os.environ["TABLE_ACTION"]
output_bucket = os.environ["OUTPUT_BUCKET"]
chat_url = os.environ["CHAT_URL"]

dynamo = boto3.resource("dynamodb")
table = dynamo.Table("lakeformation-permissions-state")
ram = boto3.client("ram")
lf = boto3.client("lakeformation")
s3 = boto3.client("s3")

def delete_event(event, context):
    LOGGER.info(f"EVENT: {event}")
    LOGGER.info(f"CONTEXT: {context}")

    if len(event['input']["DeleteTable"]) < 1:
        return 0

    total_changes = 0
    for e in event['input']["DeleteTable"]:
        dbname = e["databaseName"]
        tbname = e["tableName"]
        LOGGER.info(f"DATABASE: {dbname}")
        LOGGER.info(f"TABLE: {tbname}")

        try:
            table_check = json.loads(
                s3.get_object(Bucket=bucket, Key=f"{type_path}/{dbname}_{tbname}.json")[
                    "Body"
                ]
                .read()
                .decode()
            )["tableType"]

            s3.delete_object(Bucket=bucket, Key=f"{type_path}/{dbname}_{tbname}.json")
        except:
            LOGGER.info("No table check object found. No futher action...")
            continue
        if table_check == "virtual_view":
            LOGGER.info("View was deleted. No further action...")
            continue
        else:
            LOGGER.info("This table is not a view. Continuing with deletion cleanup...")

        actions = DeleteActions(database=dbname, table=tbname).run_queries()
        LOGGER.info(f"QUERIES: {actions.show()}")

        time.sleep(5)

        perms = actions.build_permission_state()
        filename = str(uuid.uuid4()) + ".json"
        s3PermsObj = s3.put_object(
            Bucket=bucket,
            Key=f"{saved_state_path}/{filename}",
            Body=bytes(json.dumps(perms).encode()),
        )
        LOGGER.info(s3PermsObj)
        resp = table.put_item(
            Item={"tableName": tbname, "databaseName": dbname, "fileName": filename}
        )
        LOGGER.info(f"DYNAMODB RESPONSE: {resp}")

        LOGGER.info(
            "Can't retrieve table info because it was removed from Glue... Submitting query to table_location_paths Athena table..."
        )

        path_arn = actions.get_table_path()
        LOGGER.info(f"DEREGISTERING ARN: {path_arn}")

        resource_resp = lf.deregister_resource(ResourceArn=path_arn)
        LOGGER.info(resource_resp)

        share = actions.get_share()

        ramShare = ram.disassociate_resource_share(
            resourceShareArn=share[0], resourceArns=[share[1]]
        )
        LOGGER.info(ramShare)

        # Write to cross account

        r_share = {"database": dbname, "table": tbname, "action": "DeleteTable"}

        ## Some Comment
        filename = "cross_account_objects/" + str(uuid.uuid4()) + ".json"
        resp = s3.put_object(
            Bucket=output_bucket,
            Key=filename,
            Body=bytes(json.dumps(r_share).encode()),
            ACL="bucket-owner-full-control",
        )
        total_changes += 1

        # Send message to chat
        chat_resp = chat.messenger(
            event_type="DeleteTable",
            database=dbname,
            table=tbname,
            statelogs=event["execName"],
            stream=context.log_stream_name,
            chatUrl=chat_url
        )
        LOGGER.info(chat_resp)

    return total_changes

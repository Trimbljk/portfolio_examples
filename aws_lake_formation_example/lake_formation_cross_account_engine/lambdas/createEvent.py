import boto3
import logging
import os
import json
from lambdas.utils import PermissionsObject, baseRoles
import uuid
from lambdas import chat

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

dynamo = boto3.resource("dynamodb")
table = dynamo.Table("lakeformation-permissions-state")
glue = boto3.client("glue")
lf = boto3.client("lakeformation")
s3 = boto3.client("s3")

output_bucket = os.environ["OUTPUT_BUCKET"]
lambdaRole = os.environ["ADD_LAMBDA_ROLE"]
bucket = os.environ["BUCKET_NAME"]
saved_state_path = os.environ["SAVED_STATE"]
table_action_path = os.environ["TABLE_ACTION"]
chat_url = os.environ["CHAT_URL"]
LOGGER.info(f"LAMBDA_ROLE: {lambdaRole}")
LOGGER.info(f"BASE_ROLES: {baseRoles}")
baseRoles["lambda"] = lambdaRole

def create_event(event, context):
    """This function processes any new tables created in glue. It checks for old permissions from dynamodb since tables don't hold their permissions in state. The dynamodb table holds state. The dynamodb table captures key values and uses s3 as a storage location for the values and permissions"""
    LOGGER.info(f"EVENT: {event}")
    LOGGER.info(f"CONTEXT: {context}")

    if len(event['input']["CreateTable"]) < 1:
        return 0

    total_changes = 0

    for e in event['input']["CreateTable"]:
        dbname = e["databaseName"]
        tbname = e["tableName"]

        LOGGER.info(f"DATABASE: {dbname}")
        LOGGER.info(f"TABLE: {tbname}")

        LOGGER.info("Checking for SAVED STATE lakeformation permissions...")
        lf_perm_grants = []
        item = ""
        try:
            item = table.get_item(Key={"tableName": tbname, "databaseName": dbname})[
                "Item"
            ]
            LOGGER.info(item)
        except:
            LOGGER.info("No item was returned... Applying base permissions")

        if item != "":
            getPermsObj = json.loads(
                s3.get_object(
                    Bucket=bucket, Key=f"{saved_state_path}/{item['fileName']}"
                )["Body"]
                .read()
                .decode()
            )
            s3.delete_object(
                Bucket=bucket, Key=f"{saved_state_path}/{item['fileName']}"
            )

            for perms in getPermsObj["permissions"]:
                LOGGER.info(perms)
                if "grants" in list(perms.keys()):
                    permission_spec = PermissionsObject(
                        database=dbname,
                        table=tbname,
                        arn=perms["arn"],
                        perms=perms["permissions"],
                        grants=perms["grants"],
                    ).add()
                    lf_perm_grants.append(permission_spec)
                else:
                    permission_spec = PermissionsObject(
                        database=dbname,
                        table=tbname,
                        arn=perms["arn"],
                        perms=perms["permissions"],
                    ).add()
                    lf_perm_grants.append(permission_spec)

            get_length = len(lf_perm_grants)
            LOGGER.info(f"NUMBER OF PERMISSION TO APPLY: {get_length}")
            if get_length > 20:
                LOGGER.info(
                    "Limit of 20 permissions can be applied at a time. Splitting..."
                )
                makeListofLists = lambda ls, sz: [
                    ls[i : i + sz] for i in range(0, len(ls), sz)
                ]
                lol = makeListofLists(lf_perm_grants, 20)
                count = 1
                for permList in lol:
                    LOGGER.info(f"Applying SAVED STATE Permissions set {count}...")
                    response = lf.batch_grant_permissions(Entries=permList)
                    if len(response["Failures"]) < 1:
                        LOGGER.info(
                            f"Successfully applied permissions in set {count}..."
                        )
                        count += 1
                    else:
                        LOGGER.info(
                            f"There was a failure adding permissions to TABLE: {tbname} in DATABASE: {dbname}. EXITING..."
                        )
                        #### SEND SOMETHING TO CHAT HERE. Needs to include the EVENT
                        return
            else:
                LOGGER.info("Applying SAVED STATE Permissions...")
                response = lf.batch_grant_permissions(Entries=lf_perm_grants)
                LOGGER.info(response)
                if len(response["Failures"]) < 1:
                    LOGGER.info(f"Successfully applied SAVED STATE permissions set...")
                else:
                    LOGGER.info(
                        f"There was a failure adding SAVED STATE permissions to TABLE: {tbname} in DATABASE: {dbname}. EXITING..."
                    )
                    #### SEND SOMETHING TO CHAT HERE
                    return
        else:
            entries = []
            for key, role in baseRoles.items():
                if e["tableType"] == "virtual_view" and key == "org":
                    pass
                else:
                    entries.append(
                        PermissionsObject(
                            database=dbname,
                            table=tbname,
                            arn=role,
                            perms=["SELECT", "DESCRIBE"],
                        ).add()
                    )
            response = lf.batch_grant_permissions(Entries=entries)
            LOGGER.info(response)
            if len(response["Failures"]) < 1:
                LOGGER.info(f"Successfully applied base permissions...")
            else:
                LOGGER.info(
                    f"There was a failure adding permissions to TABLE: {tbname} in DATABASE: {dbname}. EXITING..."
                )
                return
                #### SEND SOMETHING TO CHAT HERE
        if e["tableType"] == "virtual_view":
            LOGGER.info("Added permissions to view. No further processing...")
            continue

        LOGGER.info("Retrieving registered S3 resource paths...")

        get_s3_resources = lf.list_resources()["ResourceInfoList"]
        resource_list = []
        for resource in get_s3_resources:
            set_arn = resource["ResourceArn"].split(":::")[1]
            resource_list.append(set_arn)

        LOGGER.info("Checking for S3 path registration...")
        table_s3_path = e["storageLocation"].split("//")[1]
        LOGGER.info(f"RESOURCE TO REGISTER: {table_s3_path}")
        if table_s3_path in resource_list:
            LOGGER.info("Resource already shared...")
        else:
            try:
                LOGGER.info("Adding new resource location to lakeformation...")
                lf_response = lf.register_resource(
                    ResourceArn=f'arn:aws:s3:::{table_s3_path.rstrip("/")}',
                    UseServiceLinkedRole=True,
                )
                LOGGER.info(
                    f"LAKE FORMATION REGISTERED RESOURCE RESPONSE: {lf_response}"
                )

            except:
                LOGGER.info(
                    f"EXCEPTION: There was an error when registering the path: {table_s3_path}..."
                )

        # Write to cross account
        r_share = {"database": dbname, "table": tbname, "action": "CreateTable"}
        filename = "cross_account_objects/" + str(uuid.uuid4()) + ".json"
        resp = s3.put_object(
            Bucket=output_bucket,
            Key=filename,
            Body=bytes(json.dumps(r_share).encode()),
            ACL="bucket-owner-full-control",
        )
        LOGGER.info("Writing info to dev bucket...")
        LOGGER.info(f"Response from dev: {resp}")
        total_changes += 1

        # Send message to chat
        chat_resp = chat.messenger(
            event_type="CreateTable",
            database=dbname,
            table=tbname,
            statelogs=event["execName"],
            stream=context.log_stream_name,
            chatUrl=chat_url
        )
        LOGGER.info(chat_resp)

    return total_changes

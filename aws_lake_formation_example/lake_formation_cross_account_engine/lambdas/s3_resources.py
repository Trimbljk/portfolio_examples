import boto3
import logging
import os
import json

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
bucket = os.environ["BUCKETNAME"]
s3_path = os.environ["S3_PATH"]
tables_path = os.environ["TABLES_PATH"]
resource_path = os.environ["RESOURCE_PATH"]

lf = boto3.client("lakeformation")
glue = boto3.client("glue")
s3 = boto3.client("s3")
ram = boto3.client("ram")


def resource_share():
    at = ram.get_resource_share_associations(
        associationType="RESOURCE", associationStatus="ASSOCIATED"
    )

    records = []
    for share in at["resourceShareAssociations"]:
        records.append(
            {
                "arn": share["resourceShareArn"],
                "resource_share_name": share["resourceShareName"],
                "associated_entity": share["associatedEntity"],
            }
        )

    table_records = [json.dumps(record) for record in records]
    resp = s3.put_object(
        Bucket=bucket,
        Key=f"{resource_path}/resource_shares.json",
        Body=bytes("\n".join(table_records).encode()),
    )
    LOGGER.info(f"REOURCE SHARE RESP: {resp}")

    return {
        "statusCode": 200,
        "body": json.dumps("Finished uploading resource_share data!"),
    }


def get_all_table_info():
    db_names = []
    dbs = glue.get_databases()["DatabaseList"]
    for db in dbs:
        db_names.append(db["Name"])
        LOGGER.info(db["Name"])

    tbs = []
    for db in db_names:
        LOGGER.info(f"getting tables...{db}")
        tables = glue.get_tables(DatabaseName=db)["TableList"]
        for tab in tables:
            LOGGER.info(tab)
            tbs.append(
                {
                    "table_name": tab["Name"],
                    "table_location_path": tab["StorageDescriptor"]["Location"],
                    "database_name": db
                }
            )
    table_records = [json.dumps(record) for record in tbs]
    resp = s3.put_object(
        Bucket=bucket,
        Key=f"{tables_path}/table_location_paths.json",
        Body=bytes("\n".join(table_records).encode()),
    )

    LOGGER.info(f"TABLE LOCATION INFORMATION: {resp}")
    return {
        "statusCode": 200,
        "body": json.dumps("Finished uploading table path data!"),
    }


def build_tables(event, context):
    LOGGER.info("Create TABLES PATH table...")
    f1 = get_all_table_info()
    LOGGER.info(f1)

    LOGGER.info("Creating RESOURCE SHARE table...")
    f2 = resource_share()
    LOGGER.info(f2)

    LOGGER.info("Creating REGISTERED S3 RESOURCES table...")
    get_resources = lf.list_resources()["ResourceInfoList"]
    resource_list = []
    for res in get_resources:
        fullpath = res["ResourceArn"].split(":::")[1]
        rec = {
            "arn": res["ResourceArn"],
            "bucket": fullpath.split("/")[0],
            "data_path": fullpath,
        }
        resource_list.append(rec)

    records = [json.dumps(record) for record in resource_list]

    resp = s3.put_object(
        Bucket=bucket,
        Key=f"{s3_path}/s3_resources.json",
        Body=bytes("\n".join(records).encode()),
    )

    LOGGER.info(f"REGISTERED RESOURCES: {resp}")
    return {"statusCode": 200, "body": json.dumps("Finished uploading resource_data!")}

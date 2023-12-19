import boto3
import json
import os
import logging
import re
import uuid
#https://chat.googleapis.com/v1/spaces/AAAAGg94VBo/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=EdZsB0_V0ERhMT_0LIipTs8vdrz2Shhm2-UAySwZpNc

bucket = os.environ["BUCKET"]

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
LOGGER.info(f"BUCKET SOURCE: {bucket}")

ram = boto3.client("ram")
s3 = boto3.client("s3")
glue = boto3.client("glue")
lf = boto3.client("lakeformation")


def engine(event, context):
    LOGGER.info(event)

    linkData = json.loads(
        s3.get_object(Bucket=bucket, Key=event["detail"]["object"]["key"])["Body"]
        .read()
        .decode()
    )

    LOGGER.info(linkData)
    database = linkData['database']
    table = linkData['table']

    if linkData["action"] == "DeleteTable":

        LOGGER.info(f"DATABASE: {linkData['database']}")
        LOGGER.info(f"TABLE: {linkData['table']}")
        LOGGER.info("REMOVING TABLE...")
        resp = glue.delete_table(DatabaseName=database, Name=table)

    elif linkData["action"] == "CreateTable":
        create = glue.create_table(
            DatabaseName=database,
            TableInput={
                "Name": linkData["table"],
                "TargetTable": {
                    "CatalogId": "",
                    "DatabaseName": linkData["database"],
                    "Name": linkData["table"],
                },
            },
        )
        LOGGER.info(f"GLUE RESPONSE: {create}")
        LOGGER.info("ADDING PERMISSIONS")

        add_perms = lf.batch_grant_permissions(
            Entries=[
                {
                    "Id": str(uuid.uuid4()),
                    "Principal": {
                       need to add a principal here 
                    },
                    "Resource": {
                        "Table": {
                            "CatalogId": "",
                            "DatabaseName": database,
                            "Name": table,
                        }
                    },
                    "Permissions": ["DROP"],
                }
            ]
        )

    try:
        delete_file = s3.delete_object(
            Bucket=bucket, Key=event["detail"]["object"]["key"]
        )
        LOGGER.info(delete_file)
    except:
        LOGGER.info(f"Issue deleting key...")

    return "200"

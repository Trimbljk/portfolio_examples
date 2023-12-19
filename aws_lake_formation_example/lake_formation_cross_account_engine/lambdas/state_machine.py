import boto3
import json
import os
import logging
import uuid
from lambdas.utils import EventSorter

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

sfn = boto3.client("stepfunctions")
s3 = boto3.client("s3")

bucket = os.environ["BUCKET"]
prefix = os.environ["OUTPUT_PATH"]
sfnArn = os.environ["STATE_MACHINE"]

LOGGER.info(f"BUCKET: {bucket}")
LOGGER.info(f"PREFIX: {prefix}")
LOGGER.info(f"STATE_MACHINE: {sfnArn}")


def trigger(event, context):
    LOGGER.info(f"EVENT: {event}")

    getObjNames = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)

    LOGGER.info(getObjNames)

    if getObjNames["KeyCount"] == 0:
        return "No table actions to process. Exiting..."
    keylist = []
    for i in getObjNames["Contents"]:
        keylist.append(i["Key"])
        LOGGER.info(i["Key"])

    LOGGER.info(f"KEYLIST: {keylist}")

    allEvents = []
    for filename in keylist:
        eventObj = json.loads(
            s3.get_object(Bucket=bucket, Key=filename)["Body"].read().decode()
        )
        allEvents.append(eventObj)

    sfnData = EventSorter(allEvents).table_queues()
    LOGGER.info(sfnData)

    for action in sfnData["CreateTable"]:
        resp = s3.put_object(
            Bucket=bucket,
            Key=f"table_type_path/{action['databaseName']}_{action['tableName']}.json",
            Body=bytes(json.dumps(action).encode()),
        )
    for key in keylist:
        s3.delete_object(Bucket=bucket, Key=key)

    if any(len(v) > 0 for k, v in sfnData.items()):
        pass
    else:
        return "No table actions to process. Exiting..."

    sfnBody = json.dumps(sfnData)
    LOGGER.info(f"EVENT_BODY: {sfnBody}")

    executionName = "Starting_LF_Engine" + "-" + str(uuid.uuid4())
    machineStart = response = sfn.start_execution(
        stateMachineArn=sfnArn, name=executionName, input=sfnBody
    )
    LOGGER.info(f"STATE_MACHINE Status Code: {machineStart}")

    return sfnData

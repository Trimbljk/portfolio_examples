import boto3
import logging

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

lf = boto3.client('lakeformation')

def create_table(event, context):

    LOGGER.info(event)

    return "200"



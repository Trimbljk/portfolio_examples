import logging
import boto3
import json
import os
import time

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)
bucket = os.environ["BUCKET"]

s3 = boto3.client("s3")
athena = boto3.client("athena")
query = """create table lakeformation.example_test with (parquet_compression = 'SNAPPY') as 
select gtdb.aim, gtdb.asm, binomial 
from genomics.gtdbtk_parquet as gtdb 
inner join genomics.checkm_o2_parquet as checkm on gtdb.asm = checkm.asm 
where binomial is not null and completeness >= 85 and contamination <= 10 limit 10
    """
def create_table(event, context):

    ath = athena.start_query_execution(
        QueryString=query,
    ResultConfiguration={
        "OutputLocation": "s3://somebucket-lf-example/some_path/"
    },
    WorkGroup='primary'
    )

    return ath


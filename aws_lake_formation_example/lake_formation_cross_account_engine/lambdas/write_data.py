import boto3
import json
import os
import logging

bucket = os.environ["BUCKETNAME"]
LOGGER.info(f"BUCKET: {bucket}")
output_path = os.environ["PERMISSIONS_PATH"]
LOGGER.info(f"PATH: {output_path}")


def write_data(event, context):                                                                                                            
    
    final_dict = event['permissions']

    new_data = [dict(zip(final_dict.keys(), i)) for i in zip(*final_dict.values())]
    result = [json.dumps(record) for record in new_data]

    resp = s3.put_object(
        Bucket=bucket,
        Key=f"{output_path}/lakeformation_permissions.json",
        Body=bytes('\n'.join(result).encode()),
    )   
    return {
        'statusCode': 200,
        'body': json.dumps('Finished uploading data!')
    } 

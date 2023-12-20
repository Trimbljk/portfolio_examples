from os import getenv

STAGING_BUCKET = getenv(
    "ATHENA_STAGING_BUCKET",
    "s3://aws-athena-query-results-728348960442-us-west-2",
)

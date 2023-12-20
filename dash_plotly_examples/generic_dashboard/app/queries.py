from constants import STAGING_BUCKET
from pyathena import connect
from pyathena.pandas_cursor import PandasCursor


def query2df(query):
    cursor = connect(
        s3_staging_dir=STAGING_BUCKET,
        region_name="us-west-2",
        cursor_class=PandasCursor,
    ).cursor()
    df = cursor.execute(query).as_pandas()
    return df

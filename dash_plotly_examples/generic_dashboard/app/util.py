import os
import re

from constants import STAGING_BUCKET
from pyathena import connect
from pyathena.pandas.cursor import PandasCursor

BASE_PATHNAME = os.environ["BASE_PATHNAME"]


def parse_input(input_str, delim=r"\s+"):
    items = re.split(delim, input_str.rstrip())
    ids = []
    for item in items:
        item = item.lower()
        if item.isdigit():
            ids.append(int(item))
        elif item.startswith("aim"):
            i = item.replace("aim", "")
            assert i.isdigit()
            ids.append(int(i))
        else:
            raise ValueError
    ids = set(ids)  # remove duplicates
    ids = list(ids)
    return ids


def query2df(query):
    cursor = connect(
        s3_staging_dir=STAGING_BUCKET,
        region_name="us-west-2",
        cursor_class=PandasCursor,
    ).cursor()
    df = cursor.execute(query).as_pandas()
    return df


columns = (
    "aim, restriction, project_id, date_restricted, "
    "is_restricted, is_screenable, notes, "
    "primary_documentation_url, supplemental_documentation_url"
)


def set_query(inputs=None, col=columns):

    if inputs is None:
        query = (
            f"""SELECT {col} FROM restricted_use.restricted_microbe_metadata"""
        )
    if inputs is not None:
        if len(inputs) > 1:
            query = f"""
            SELECT {col} FROM restricted_use.restricted_microbe_metadata
            WHERE aim IN {tuple(inputs)};
            """
        elif len(inputs) == 1:
            single = inputs[0]
            query = f"""
            SELECT {col} FROM restricted_use.restricted_microbe_metadata
            WHERE aim = {single};
            """

    return query

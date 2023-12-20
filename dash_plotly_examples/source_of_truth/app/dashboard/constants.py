from os import environ, getenv
from typing import Final

import plotly.graph_objs as go

ATHENA_STAGING_BUCKET: Final[str] = getenv("ATHENA_STAGING_BUCKET", "")
REDIS_HASH_NAME: Final[str] = getenv("DASH_APP_NAME", "herbicides")
REDIS_URL: Final[str] = environ["REDIS_URL"]
BASE_PATHNAME: Final[str] = environ["BASE_PATHNAME"]

LARGE_DATATABLE_SIZE: Final[int] = 20

UNCHECK = "☐"
CHECK = "☑"

NULL_GRAPH = go.Figure(data=[go.Scatter(x=[1, 2, 3], y=[4, 1, 2])])

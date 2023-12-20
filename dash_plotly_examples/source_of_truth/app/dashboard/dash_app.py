import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import dcc, html
from dash.dependencies import Input, Output, State

from . import biologicals, decisions, genomics, origins, traits
from .constants import BASE_PATHNAME
from .navbar import FOOTER, navbar

external_scripts = ["https://kit.fontawesome.com/733aa7d60f.js"]

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    external_scripts=external_scripts,
    url_base_pathname=BASE_PATHNAME,
)

app.title = "ecosystem"
server = app.server  # this is required for gunicorn

biologicals.callbacks(app)

TITLE = dbc.Row(
    justify="center",
    children=[
        html.Div(
            children=[
                html.H1(
                    children=[
                        html.Em("Welcome to the Dashboard Ecosystem"),
                    ]
                )
            ],
        )
    ],
)

TABS = dbc.Row(
    children=[
        dbc.Col(
            children=[
                dcc.Tabs(
                    parent_style={"width": "100%"},
                    content_style={
                        "width": "100%",
                        "border-left": "1px solid #d6d6d6",
                    },
                    className="custom-tabs-container",
                    children=[
                        origins.tab(app),
                        genomics.tab(app),
                        decisions.tab(app),
                        biologicals.tab(),
                        traits.tab(),
                    ],
                    vertical=True,
                )
            ],
        )
    ]
)

app.layout = html.Div(
    className="container-fluid",
    children=[
        navbar(app.get_asset_url("agbiome.png")),
        # TITLE,
        TABS,
        dbc.Row(
            dbc.Col(
                FOOTER,
                width=12,
            )
        ),
    ],
)


@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

import dash_bootstrap_components as dbc
from dash import dcc, html


def tab():
    base_id = "traits"

    return dcc.Tab(
        label="Traits",
        className="custom-tab",
        selected_className="custom-tab--selected",
        children=[
            html.Div(className="container-fluid", children=[html.H1("Traits")])
        ],
    )

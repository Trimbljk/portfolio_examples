import dash_bootstrap_components as dbc
from dash import dcc, html


def tab(base_id: str):
    base_id = f"{base_id}-inventory"

    return dcc.Tab(
        label="Inventory",
        className="custom-tab",
        selected_className="custom-tab--selected",
        children=[
            html.Div(
                className="container-fluid",
                children=[html.H1("Project Inventory")],
            )
        ],
    )

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dashboard import data, util
from . import (
    assay_status,
    decisions,
    inventory,
    leads,
    visualize,
    workflow,
    working_set,
)

base_id = "biologicals"


def tab():
    return dcc.Tab(
        label="Biologicals",
        className="custom-tab",
        selected_className="custom-tab--selected",
        children=[
            html.Div(
                className="container-fluid",
                children=[
                    header(base_id),
                    tabs(base_id),
                ],
            )
        ],
    )


def display_working_set(n: int, is_open: bool):
    if n:
        return not is_open
    return is_open


def callbacks(app):
    assay_status.callbacks(app)
    visualize.callbacks(app)
    working_set.callbacks(app)

    @app.callback(
        Output("working-set-modal", "is_open"),
        [
            Input("biologicals-view-set-button", "n_clicks"),
        ],
        [State("working-set-modal", "is_open")],
    )
    def handle(n, is_open):
        return display_working_set(n, is_open)


def header(base_id: str):
    dm = data.DataManager()

    return dbc.Row(
        children=[
            dbc.Col(
                util.selection(
                    values=dm.projects(),
                    selector_id=f"{base_id}-project-selector",
                    label="Select a Project",
                ),
                width=4,
            ),
            dbc.Col(
                dbc.Button(
                    "View Working Set",
                    id=f"{base_id}-view-set-button",
                    className="float-end",
                    color="primary",
                    outline=True,
                ),
            ),
        ],
        style={"margin-bottom": "2em"},
    )


def tabs(base_id: str):
    return dbc.Row(
        children=[
            dbc.Col(
                dcc.Tabs(
                    parent_className="custom-tabs",
                    className="custom-tabs-contaimer",
                    children=[
                        assay_status.tab(base_id),
                        visualize.tab(base_id),
                        decisions.tab(base_id),
                        leads.tab(base_id),
                        inventory.tab(base_id),
                        workflow.tab(base_id),
                    ],
                ),
            ),
            working_set.working_set_modal(),
            working_set.working_set_decision_modal(),
        ]
    )

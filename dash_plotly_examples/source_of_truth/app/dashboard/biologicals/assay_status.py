import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go
from dash import dash_table, dcc, html
from dash.dependencies import Input, Output, State
from dashboard import constants, data, util

base_id_modifier = "assay-status"


def tab(base_id: str):
    base_id = f"{base_id}-{base_id_modifier}"

    return dcc.Tab(
        label="Assay Status",
        className="custom-tab",
        selected_className="custom-tab--selected",
        children=[
            html.Div(
                className="container-fluid",
                children=[
                    selection(base_id),
                    dbc.Row(
                        dbc.Col(
                            all_time(base_id),
                        )
                    ),
                    graphs(base_id),
                    filters(base_id),
                    filter_button(base_id),
                    data_table(base_id),
                ],
            )
        ],
    )


def callbacks(app):
    @app.callback(
        Output("biologicals-assay-status-assay-selector", "options"),
        Input("biologicals-project-selector", "value"),
        prevent_initial_call=True,
    )
    def populate_assay_selection(project: str):
        dm = data.DataManager()

        assays = dm.assays(project)
        if assays is None:
            return dash.no_update

        return assays

    @app.callback(
        Output("biologicals-assay-status-datatable", "data"),
        Output("biologicals-assay-status-datatable", "columns"),
        Input("biologicals-assay-status-assay-selector", "value"),
        State("biologicals-project-selector", "value"),
        prevent_initial_call=True,
    )
    def populate_datatables(assay: str, project: str):
        dm = data.DataManager()
        df = dm.table_data(project, assay)
        table_data = []
        if df is not None:
            table_data = df.to_dict("records")
        cols = dm.table_columns(project, assay)
        if cols is None:
            cols = []

        return table_data, cols

    @app.callback(
        Output("biologicals-assay-status-graph-a", "figure"),
        Input("biologicals-assay-status-assay-selector", "value"),
        State("biologicals-project-selector", "value"),
        prevent_initial_call=True,
    )
    def populate_graph_a(assay: str, project: str):
        dm = data.DataManager()
        df = dm.table_data(project, assay)
        if df is None:
            return constants.NULL_GRAPH

        charts = dm.charts(project, assay)
        if charts is None:
            return constants.NULL_GRAPH

        return go.Figure(
            data=[go.Scatter(x=df[charts[0]["x"]], y=df[charts[0]["y"]])],
            layout={"title": charts[0]["title"]},
        )


def selection(base_id: str):
    return dbc.Row(
        dbc.Col(
            util.selection(
                values=[],
                selector_id=f"{base_id}-assay-selector",
                label="Select Assay",
                style={"margin-bottom": "1.5rem"},
            ),
            width=4,
        )
    )


def all_time(base_id: str):
    return dash_table.DataTable(
        data=[
            {
                "Initial Activity Rate": "ALL TIME 1.9%",
                "Confirmation 1 Activity Rate": "ALL TIME 4.0%",
                "Purity Activity Rate": "ALL TIME 77.1%",
                "Hit Rate": "all time 0.5%",
            }
        ],
        id=f"{base_id}-all-time-datatable",
    )


def graphs(base_id: str):
    return dbc.Row(
        children=[
            dbc.Col(
                dcc.Graph(
                    id=f"{base_id}-graph-a",
                    figure=go.Figure(
                        data=[go.Scatter(x=[1, 2, 3], y=[4, 1, 2])],
                    ),
                ),
                width=6,
            ),
            dbc.Col(
                dcc.Graph(
                    id=f"{base_id}-graph-b",
                    figure=go.Figure(
                        data=[go.Scatter(x=[1, 2, 3], y=[4, 1, 2])],
                    ),
                ),
                width=6,
            ),
        ],
    )


def filters(base_id: str):
    return html.Div(
        dbc.Row(
            children=[
                dbc.Col(
                    children=[
                        util.date_filter(base_id, "date-filter", "Assay Date"),
                        util.selection(
                            values=["Hypothesis 123", "Option 2"],
                            selector_id=f"{base_id}-hypothesis-dropdown",
                            label="",
                        ),
                    ],
                    width=6,
                ),
                dbc.Col(
                    children=[
                        util.selection(
                            values=["AIM", "ASM", "AIC", "AES"],
                            selector_id=f"{base_id}-id-dropdown",
                            label="Identified by:",
                            style={"margin-bottom": "1.5em"},
                        ),
                        dbc.Textarea(
                            id=f"{base_id}-id-paste",
                            className="h-100",
                            draggable=False,
                            disabled=False,
                            placeholder="Paste a list of IDs",
                        ),
                    ],
                    width=6,
                ),
            ]
        ),
        id=f"{base_id}-filters",
        style={
            "margin-bottom": "1.5rem",
            "border-color": "black",
            "border-style": "solid",
            "border-width": "2px",
            "padding-bottom": "7.5rem",
            "padding-left": "1.5rem",
            "padding-right": "1.5rem",
        },
    )


def filter_button(base_id: str):
    return dbc.Row(
        dbc.Col(
            html.Button(
                "Filter Datatable",
                style={"float": "right"},
            ),
        ),
    )


def data_table(base_id: str):
    columns = [
        {
            "name": "Sample ID",
            "id": "sample_id",
            "hideable": False,
        },
        {
            "name": "Score Date",
            "id": "score_date",
            "hideable": True,
        },
        {
            "name": "Media",
            "id": "media",
            "hideable": True,
        },
        {
            "name": "Number Dead",
            "id": "number_dead",
            "hideable": True,
        },
        {
            "name": "Total Insects",
            "id": "total_insects",
            "hideable": True,
        },
    ]

    return dbc.Row(
        dbc.Col(
            dash_table.DataTable(
                id=f"{base_id}-datatable",
                columns=columns,
                merge_duplicate_headers=True,
                markdown_options={"html": True},
                editable=False,
                filter_action="custom",
                sort_action="custom",
                sort_by=[{"column_id": "sample_id", "direction": "asc"}],
                row_deletable=False,
                page_action="custom",
                persistence_type="memory",
                page_current=0,
                page_size=constants.LARGE_DATATABLE_SIZE,
                style_table={
                    "overflowX": "auto",
                    "paddingRight": "1px",
                    "minWidth": "100%",
                    "minHeight": 1100,
                    "height": 1100,
                },
                style_header={
                    "whiteSpace": "normal",
                    "height": "auto",
                    "backgroundColor": "rgba(220, 220, 220, 0)",
                    "fontWeight": "600",
                    "border": "0px 0px 2px 0px",
                    "borderColor": "#151515",
                    "textAlign": "left",
                    "verticalAlign": "bottom",
                },
                style_data_conditional=[
                    {
                        "if": {"row_index": "odd"},
                        "backgroundColor": "rgb(238, 238, 238)",
                    },
                ],
                style_cell={
                    "fontFamily": (
                        "'Helvetica Neue', Helvetica, Arial, sans-serif"
                    ),
                    "fontSize": "14px",
                    "paddingRight": "15px",
                    "paddingLeft": "15px",
                    "textAlign": "left",
                    "minWidth": "120px",
                    "maxWidth": "800px",
                    "textOverflow": "ellipsis",
                    "overflow": "hidden",
                    "overflowWrap": "break-word",
                    "wordWrap": "break-word",
                },
                persistence=True,
                css=[
                    {
                        "selector": ".dash-spreadsheet-menu",
                        "rule": "float: left",
                    },
                ],
            ),
        ),
    )

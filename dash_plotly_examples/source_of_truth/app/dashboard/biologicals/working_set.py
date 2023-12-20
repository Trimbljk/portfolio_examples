from datetime import date

import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State


def display_working_set_decision_modal(n: int, is_open: bool):
    if n:
        return not is_open
    return is_open


def callbacks(app):
    @app.callback(
        [
            Output("working-set-decision-modal", "is_open"),
            Output("working-set-modal", "is_open", allow_duplicate=True),
        ],
        [
            Input("working-set-decision-open", "n_clicks"),
        ],
        [State("working-set-decision-modal", "is_open")],
        prevent_initial_call=True,
    )
    def handle(n, is_open):
        return display_working_set_decision_modal(n, is_open), False


def working_set_modal():
    return dbc.Modal(
        id="working-set-modal",
        fullscreen=True,
        children=[
            dbc.ModalHeader("Current working items", close_button=True),
            dbc.ModalBody(
                className="printable",
                children=[
                    dcc.Loading(
                        fullscreen=True,
                        children=[
                            dbc.Row(
                                dbc.Col(
                                    children=[
                                        html.H2(
                                            "These items are your current working "
                                            "set."
                                        ),
                                        html.P(
                                            "You can use them to filter other "
                                            "dashboards or capture a decision "
                                            "about them"
                                        ),
                                    ]
                                )
                            ),
                            dbc.Row(
                                dbc.Col(
                                    dbc.Table(
                                        id="working-set",
                                        bordered=True,
                                        children=[
                                            html.Thead(
                                                html.Tr(
                                                    children=[
                                                        html.Th("Identifier"),
                                                        html.Th("Taxonomy"),
                                                        html.Th(
                                                            "Taxonomy Method"
                                                        ),
                                                        html.Th("Select"),
                                                    ]
                                                )
                                            ),
                                            html.Tbody(
                                                id="barcode-match-display",
                                                children=[
                                                    html.Tr(
                                                        children=[
                                                            html.Td(
                                                                "AIM000123"
                                                            ),
                                                            html.Td(
                                                                "B. cereus"
                                                            ),
                                                            html.Td("btyper"),
                                                            html.Td(
                                                                dbc.Checkbox()
                                                            ),
                                                        ]
                                                    ),
                                                    html.Tr(
                                                        children=[
                                                            html.Td(
                                                                "AIM000456"
                                                            ),
                                                            html.Td(
                                                                "B. cereus"
                                                            ),
                                                            html.Td("btyper"),
                                                            html.Td(
                                                                dbc.Checkbox()
                                                            ),
                                                        ]
                                                    ),
                                                    html.Tr(
                                                        children=[
                                                            html.Td(
                                                                "AIM000789"
                                                            ),
                                                            html.Td(
                                                                "B. cereus"
                                                            ),
                                                            html.Td("btyper"),
                                                            html.Td(
                                                                dbc.Checkbox()
                                                            ),
                                                        ]
                                                    ),
                                                    html.Tr(
                                                        children=[
                                                            html.Td(
                                                                "AIM000999"
                                                            ),
                                                            html.Td(
                                                                "B. cereus"
                                                            ),
                                                            html.Td("btyper"),
                                                            html.Td(
                                                                dbc.Checkbox()
                                                            ),
                                                        ]
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                    className="printable",
                                ),
                                className="printable",
                            ),
                        ],
                    )
                ],
            ),
            dbc.ModalFooter(
                children=[
                    dbc.Button(
                        "Clear set",
                        id="clear-set",
                        className="ml-auto float-start",
                        color="danger",
                    ),
                    dbc.Button(
                        "Remove selected",
                        id="remove-selected-from-set",
                        className="ml-auto float-end",
                        color="danger",
                        outline=True,
                    ),
                    dbc.Button(
                        "Capture a decision",
                        id="working-set-decision-open",
                        className="ml-auto float-end",
                        color="primary",
                    ),
                ]
            ),
        ],
    )


def working_set_decision_modal():
    return dbc.Modal(
        id="working-set-decision-modal",
        fullscreen=True,
        children=[
            dbc.ModalHeader("Record your decision", close_button=True),
            dbc.ModalBody(
                className="printable",
                children=[
                    dcc.Loading(
                        fullscreen=True,
                        children=[
                            dbc.Row(
                                dbc.Col(
                                    children=[
                                        html.P(
                                            "Enter the details of your "
                                            "decision below"
                                        )
                                    ]
                                )
                            ),
                            dbc.Row(
                                dbc.Col(
                                    dbc.Form(
                                        id="working-set-decision-form",
                                        children=[
                                            dbc.Row(
                                                children=[
                                                    dbc.Col(
                                                        children=[
                                                            dbc.Label(
                                                                "Entity identifiers",
                                                                html_for="set-decision-identifiers-"
                                                                "input",
                                                            ),
                                                            dbc.Textarea(
                                                                id="set-decision-identifiers-input",
                                                                draggable=True,
                                                                disabled=False,
                                                                placeholder="Identifiers...",
                                                                value="AIM000123\nAIM000456\n"
                                                                "AIM000789\nAIM000999",
                                                                style={
                                                                    "min-height": "15rem",
                                                                    "margin-bottom": "1rem",
                                                                },
                                                            ),
                                                            dbc.Label(
                                                                "Tags",
                                                                html_for="set-decision-tags-input",
                                                            ),
                                                            dbc.Textarea(
                                                                id="set-decision-tags-input",
                                                                draggable=True,
                                                                disabled=False,
                                                                placeholder="Enter tags...",
                                                            ),
                                                        ],
                                                        width=6,
                                                    ),
                                                    dbc.Col(
                                                        width=6,
                                                        children=[
                                                            dbc.Row(
                                                                dbc.Col(
                                                                    children=[
                                                                        dbc.Label(
                                                                            "Step",
                                                                            html_for="set-decision-step",
                                                                        ),
                                                                        dcc.Dropdown(
                                                                            id="set-decision-step",
                                                                            value="In vitro",
                                                                            options=[
                                                                                {
                                                                                    "label": "In vitro",
                                                                                    "value": "In vitro",
                                                                                },
                                                                                {
                                                                                    "label": "Fractionation",
                                                                                    "value": "Fractionation",
                                                                                },
                                                                                {
                                                                                    "label": "Greenhouse",
                                                                                    "value": "Greenhouse",
                                                                                },
                                                                            ],
                                                                        ),
                                                                    ]
                                                                ),
                                                                style={
                                                                    "margin-bottom": "1rem"
                                                                },
                                                            ),
                                                            dbc.Row(
                                                                dbc.Col(
                                                                    children=[
                                                                        dbc.Label(
                                                                            "Decision",
                                                                            html_for="set-decision-decision",
                                                                        ),
                                                                        dcc.Dropdown(
                                                                            id="set-decision-decision",
                                                                            value="Advance",
                                                                            options=[
                                                                                {
                                                                                    "label": "Advance",
                                                                                    "value": "Advance",
                                                                                },
                                                                                {
                                                                                    "label": "Stop",
                                                                                    "value": "Stop",
                                                                                },
                                                                                {
                                                                                    "label": "Repeat",
                                                                                    "value": "Repeat",
                                                                                },
                                                                                {
                                                                                    "label": "Hold",
                                                                                    "value": "Hold",
                                                                                },
                                                                            ],
                                                                        ),
                                                                    ]
                                                                ),
                                                                style={
                                                                    "margin-bottom": "1rem"
                                                                },
                                                            ),
                                                            dbc.Row(
                                                                dbc.Col(
                                                                    children=[
                                                                        dbc.Label(
                                                                            "Criteria",
                                                                            html_for="set-decision-criteria",
                                                                        ),
                                                                        dcc.Dropdown(
                                                                            id="set-decision-decision",
                                                                            value=">80% mortality",
                                                                            options=[
                                                                                {
                                                                                    "label": ">80% mortality",
                                                                                    "value": ">80% mortality",
                                                                                },
                                                                                {
                                                                                    "label": "Atypical chlorosis",
                                                                                    "value": "Atypical chlorosis",
                                                                                },
                                                                            ],
                                                                        ),
                                                                    ]
                                                                ),
                                                                style={
                                                                    "margin-bottom": "1rem"
                                                                },
                                                            ),
                                                            dbc.Row(
                                                                dbc.Col(
                                                                    children=[
                                                                        dbc.Label(
                                                                            "Hypothesis",
                                                                            html_for="set-decision-hypothesis",
                                                                        ),
                                                                        dcc.Dropdown(
                                                                            id="set-decision-decision",
                                                                            value="Random selection",
                                                                            options=[
                                                                                {
                                                                                    "label": "Random selection",
                                                                                    "value": "Random selection",
                                                                                },
                                                                                {
                                                                                    "label": "Hypothesis 1",
                                                                                    "value": "Hypothesis 1",
                                                                                },
                                                                            ],
                                                                        ),
                                                                    ]
                                                                ),
                                                                style={
                                                                    "margin-bottom": "1rem"
                                                                },
                                                            ),
                                                            dbc.Row(
                                                                dbc.Col(
                                                                    children=[
                                                                        dbc.Label(
                                                                            "Date",
                                                                            html_for="set-decision-date",
                                                                            style={
                                                                                "padding-right": "2rem"
                                                                            },
                                                                        ),
                                                                        dcc.DatePickerSingle(
                                                                            id="before-date-picker",
                                                                            clearable=True,
                                                                            display_format="YYYY-MM-DD",
                                                                            date=date.today(),
                                                                        ),
                                                                    ]
                                                                ),
                                                                style={
                                                                    "margin-bottom": "1rem"
                                                                },
                                                            ),
                                                            dbc.Row(
                                                                dbc.Col(
                                                                    children=[
                                                                        dbc.Label(
                                                                            "Who",
                                                                            html_for="set-decision-who",
                                                                            style={
                                                                                "padding-right": "2rem"
                                                                            },
                                                                        ),
                                                                        dbc.Input(
                                                                            id="set-decision-who"
                                                                        ),
                                                                    ]
                                                                ),
                                                                style={
                                                                    "margin-bottom": "1rem"
                                                                },
                                                            ),
                                                        ],
                                                    ),
                                                ]
                                            ),
                                            dbc.Row(
                                                children=[
                                                    dbc.Col(
                                                        children=[
                                                            dbc.Label(
                                                                "Rationale",
                                                                html_for="set-decision-rationale",
                                                            ),
                                                            dbc.Textarea(
                                                                id="set-decision-rationale",
                                                                draggable=True,
                                                                disabled=False,
                                                                placeholder="Enter a description of why the decision was made...",
                                                                style={
                                                                    "min-height": "10rem",
                                                                    "margin-bottom": "1rem",
                                                                },
                                                            ),
                                                        ],
                                                    ),
                                                ]
                                            ),
                                            dbc.Row(
                                                children=[
                                                    dbc.Col(
                                                        children=[
                                                            dbc.Button(
                                                                "Attach context documents"
                                                            )
                                                        ]
                                                    )
                                                ]
                                            ),
                                        ],
                                    ),
                                    className="printable",
                                ),
                                className="printable",
                            ),
                        ],
                    )
                ],
            ),
            dbc.ModalFooter(
                children=[
                    dbc.Button(
                        "Cancel",
                        id="cancel-set-decision",
                        className="ml-auto float-end",
                        color="danger",
                        outline=True,
                    ),
                    dbc.Button(
                        "Record decision",
                        id="capture-set-decision",
                        className="ml-auto float-end",
                        color="primary",
                    ),
                ]
            ),
        ],
    )

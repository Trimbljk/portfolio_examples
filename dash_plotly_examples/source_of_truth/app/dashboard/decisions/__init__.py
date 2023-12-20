import dash_bootstrap_components as dbc
from dash import dcc, html


def tab(app):
    base_id = "decisions"

    return dcc.Tab(
        label="Decisions",
        className="custom-tab",
        selected_className="custom-tab--selected",
        children=[
            html.Div(
                className="container-fluid",
                children=[
                    html.H1("Decisions"),
                    dbc.Row(
                        dbc.Col(
                            children=[
                                html.Img(
                                    style={"width": "100%"},
                                    src=app.get_asset_url("decisions.png"),
                                )
                            ]
                        )
                    ),
                ],
            )
        ],
    )

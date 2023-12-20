import dash_bootstrap_components as dbc
from dash import dcc, html


def tab(app):
    base_id = "genomics"

    return dcc.Tab(
        label="Genomics",
        className="custom-tab",
        selected_className="custom-tab--selected",
        children=[
            html.Div(
                className="container-fluid",
                children=[
                    html.H1("Genomics"),
                    dbc.Row(
                        dbc.Col(
                            children=[
                                html.Img(
                                    style={"width": "100%"},
                                    src=app.get_asset_url("genomics.png"),
                                )
                            ]
                        )
                    ),
                ],
            )
        ],
    )

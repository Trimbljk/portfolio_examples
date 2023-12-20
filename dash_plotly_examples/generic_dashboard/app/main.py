import os

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from input_card import INPUT
from navbar import FOOTER, navbar
from util import parse_input, query2df, set_query

BASE_PATHNAME = os.environ["BASE_PATHNAME"]

external_scripts = [
    "https://kit.fontawesome.com/733aa7d60f.js",
    "https://www.googletagmanager.com/gtag/js?id=G-BQKXV2ED5K",
]

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    external_scripts=external_scripts,
    url_base_pathname=BASE_PATHNAME,
)

app.title = "restricteduse"
server = app.server  # this is required for gunicorn

df = pd.read_csv(
    (
        "https://raw.githubusercontent.com/plotly/"
        "datasets/master/hello-world-stock.csv"
    )
)

app.layout = html.Div(
    className="container",
    children=[
        dcc.Location(id="url", refresh=False),
        navbar(app.get_asset_url("agbiome.png")),
        dbc.Toast(
            "Invalid input",
            id="input-error-toast",
            header="Input error",
            is_open=False,
            dismissable=True,
            icon="danger",
            style={
                "position": "fixed",
                "top": 66,
                "right": 40,
                "width": 350,
                "zIndex": 999999,
            },
        ),
        dbc.Row(
            style={"min-height": "300px", "padding": "10px"},
            justify="center",
            children=[INPUT],
        ),
        dbc.Row(
            dbc.Col(
                width=12,
                className="mb-3 border shadow-sm bg-light",
                style={"height": "550px", "padding-top": "5px"},
                children=[dcc.Loading(id="rum-table")],
            )
        ),
        dbc.Row(
            dbc.Col(
                width=12,
                children=[FOOTER],
            )
        ),
    ],
)


@app.callback(
    Output("rum-table", "children"),
    Output("input-error-toast", "is_open"),
    Input("go-button", "n_clicks"),
    State("radio-button", "value"),
    State("input-ids", "value"),
)
def run_query(gobutton, selector, input_ids):
    final = html.Div(
        "Run a search to view the results table.",
        className="text-muted",
        style={
            "text-align": "center",
            "font-size": "2.5em",
            "margin-top": "5em",
            "color": "#6c757d !important",
            "opacity": "0.5",
        },
    )
    if gobutton is None:
        return (final, False)

    if selector == "All" and gobutton is not None:
        query = set_query(inputs=None)
        dataframe = query2df(query)
        final = dash_table.DataTable(
            columns=[{"name": i, "id": i} for i in dataframe.columns],
            data=dataframe.to_dict("records"),
            filter_action="native",
            sort_action="native",
            export_format="xlsx",
            style_data_conditional=[
                {
                    "if": {"row_index": "odd"},
                    "backgroundColor": "rgb(238, 238, 238)",
                },
                {
                    "if": {"column_id": "primary_documentation_url"},
                    "textAlign": "left",
                },
            ],
            fixed_columns={"headers": True, "data": 1},
            style_header={
                # 'backgroundColor': 'rgba(248, 249, 240)',
                "fontWeight": "600",
                "border": "0px 0px 2px 0px",
                "borderColor": "#151515",
                "min-width": "135px",
            },
            style_cell={
                "font-family": (
                    '"Helvetica Neue", Helvetica, ' "Arial, sans-serif"
                ),
                "font-size": "14px",
                "paddingRight": "15px",
                "paddingLeft": "15px",
                "overflow": "hidden",
                "textOverflow": "ellipsis",
                "min-width": "100px",
            },
            style_table={
                "maxHeight": "460px",
                "margin-top": "10px",
                "min-width": "100%",
            },
        )
    if selector == "AIM" and gobutton is None:
        raise PreventUpdate

    if selector == "AIM" and gobutton is not None:
        try:
            aims = parse_input(input_ids)
            query = set_query(inputs=aims)
            dataframe = query2df(query)
            final = dash_table.DataTable(
                columns=[{"name": i, "id": i} for i in dataframe.columns],
                data=dataframe.to_dict("records"),
                filter_action="native",
                sort_action="native",
                export_format="xlsx",
                style_data_conditional=[
                    {
                        "if": {"row_index": "odd"},
                        "backgroundColor": "rgb(238, 238, 238)",
                    },
                    {
                        "if": {"column_id": "primary_documentation_url"},
                        "textAlign": "left",
                    },
                    {"if": {"column_id": "notes"}, "textAlign": "left"},
                ],
                fixed_columns={"headers": True, "data": 1},
                style_header={
                    # 'backgroundColor': 'rgba(248, 249, 240)',
                    "fontWeight": "600",
                    "border": "0px 0px 2px 0px",
                    "borderColor": "#151515",
                    "min-width": "135px",
                },
                style_cell={
                    "font-family": (
                        '"Helvetica Neue", Helvetica, ' "Arial, sans-serif"
                    ),
                    "font-size": "14px",
                    "paddingRight": "15px",
                    "paddingLeft": "15px",
                    "overflow": "hidden",
                    "textOverflow": "ellipsis",
                    "min-width": "100px",
                },
                style_table={
                    "maxHeight": "450px",
                    "margin-top": "10px",
                    "min-width": "100%",
                    "min-height": "450px",
                },
            )
        except Exception:
            return (final, True)
    return (final, False)


@app.callback(
    Output("input-ids", "disabled"), [Input("radio-button", "value")]
)
def update_id_search(id_radio):
    if id_radio == "All":
        return True
    if id_radio == "AIM":
        return False


@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


if __name__ == "__main__":
    app.run_server(debug=True)

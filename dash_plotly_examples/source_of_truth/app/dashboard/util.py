from datetime import date

import dash_bootstrap_components as dbc
from dash import dcc, html


def selection(
    *,
    values,
    selector_id,
    label,
    help_label="",
    split_values=False,
    style={},
    multi=False,
    value=None,
):
    options = None
    if split_values:
        # prepend label to value to prevent duplicates
        options = [{"label": v[1], "value": v[1] + "." + v[0]} for v in values]
    else:
        options = [{"label": v, "value": v} for v in values]

    return html.Div(
        children=[
            dbc.Label(label, className="m-2"),
            dbc.FormText(help_label),
            dcc.Dropdown(
                id=selector_id,
                options=options,
                multi=multi,
                style={"minWidth": "24rem"},
                value=value,
            ),
        ],
        style=style,
    )


def date_filter(base_id: str, control_id: str, label):
    return html.Div(
        children=[
            dbc.Label(label, className="m-2"),
            dcc.DatePickerRange(
                style={"display": "block"},
                id=f"{base_id}-{control_id}",
                min_date_allowed=date(2010, 1, 1),
                initial_visible_month=date.today(),
                display_format="YYYY-MM-DD",
            ),
        ],
    )

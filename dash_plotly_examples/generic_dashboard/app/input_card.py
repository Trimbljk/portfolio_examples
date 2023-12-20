import dash_bootstrap_components as dbc
import dash_html_components as html

INPUT = dbc.Col(
    style={"margin-top": "20px", "margin-left": "20px"},
    lg=6,
    md=6,
    sm=9,
    xs=12,
    className="mb-3 border shadow-sm bg-light",
    children=[
        html.Div(
            children=[
                dbc.FormGroup(
                    children=[
                        html.Div(
                            style={
                                "display": "inline-flex",
                                "margin-bottom": "10px",
                                "margin-top": "10px",
                            },
                            children=[
                                dbc.RadioItems(
                                    style={"padding-top": "7px"},
                                    inline=True,
                                    value="AIM",
                                    id="radio-button",
                                    options=[
                                        {"label": "Search", "value": "AIM"},
                                        {"label": "View All", "value": "All"},
                                    ],
                                ),
                                dbc.Button(
                                    "Go",
                                    color="secondary",
                                    id="go-button",
                                    outline=True,
                                ),
                            ],
                        ),
                        html.Div(
                            dbc.Label(
                                "AIM numbers:",
                            ),
                        ),
                        dbc.Textarea(
                            id="input-ids",
                            className="h-100",
                            draggable=False,
                            disabled=False,
                            placeholder="Identifiers go here...",
                            style={
                                "margin-top": "10px",
                                "min-height": "150px",
                            },
                        ),
                    ]
                )
            ]
        )
    ],
)

# This code is being was the start of a card
# for adding RUMs to the data catalog
# ADDITION = dbc.Col(
#            style={'margin-top': '20px', 'margin-left': '20px'},
#            lg=4,
#            md=6,
#            sm=9,
#            xs=12,
#            className='mb-3',
#            children=[
#                html.
#                ]
#
#        )

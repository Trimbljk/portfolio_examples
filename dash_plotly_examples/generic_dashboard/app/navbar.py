import dash_bootstrap_components as dbc
import dash_html_components as html

SLACK_CHANNEL = "https://chat.google.com/room/AAAA8mzfMOI?cls=7"

NAV_LINKS = [
    dbc.NavItem(
        dbc.NavLink(
            className="text-agbiome-blue",
            href="https://dashboards.agbiome.cloud",
            children=[
                html.I(className="fa fa-home fa-lg"),
                html.Span("back to gallery", style={"padding-left": "6px"}),
            ],
        )
    ),
    dbc.NavItem(
        dbc.NavLink(
            className="text-agbiome-blue",
            href="https://docs.agbiome.cloud/dashboards/restricteduse.html",
            children=[
                html.I(className="fa fa-book fa-lg"),
                html.Span("docs", style={"padding-left": "6px"}),
            ],
        )
    ),
    dbc.NavItem(
        dbc.NavLink(
            className="text-agbiome-blue",
            href=SLACK_CHANNEL,
            children=[
                html.I(className="fab fa-slack fa-lg"),
                html.Span("questions?", style={"padding-left": "6px"}),
            ],
        )
    ),
]

COLLAPSIBLE_CONTENT = dbc.Row(
    className="ml-auto flex-nowrap mt-2 mt-lg-0",
    align="center",
    no_gutters=True,
    children=[dbc.Nav(children=NAV_LINKS, fill=False)],
)


def navbar(img_url):
    return dbc.Navbar(
        className="mb-4",
        children=[
            html.A(
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=img_url, height="30px")),
                        dbc.Col(
                            dbc.NavbarBrand(
                                "RestrictedUse",
                                className="ml-2 text-agbiome-gray",
                            )
                        ),
                    ],
                    align="center",
                    no_gutters=True,
                ),
                href="#",
            ),
            dbc.NavbarToggler(id="navbar-toggler"),
            dbc.Collapse(
                id="navbar-collapse",
                navbar=True,
                children=COLLAPSIBLE_CONTENT,
            ),
        ],
        color="light",
        dark=False,
    )


FOOTER = html.Div(
    className="text-center mb-3",
    style={"margin-top": "70px"},
    children=[
        html.I(style={"padding-right": "10px"}, className="fas fa-question"),
        html.A(
            className="text-agbiome-blue",
            children=[
                "Need help? Post a question on our Slack channel.",
            ],
            href=SLACK_CHANNEL,
        ),
        html.I(style={"padding-left": "10px"}, className="fab fa-slack"),
    ],
)

import dash
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import ctx, dash_table, dcc, html
from dash.dependencies import Input, Output, State
from dashboard import constants, data, util

DEFAULT_CLUSTER_SIZE = 59.7


def tab(base_id: str):
    base_id = f"{base_id}-visualize"

    return dcc.Tab(
        label="Visualize",
        className="custom-tab",
        selected_className="custom-tab--selected",
        children=[
            html.Div(
                className="container-fluid",
                children=[
                    dcc.Loading(
                        fullscreen=True,
                        children=[
                            selection(base_id),
                            graphs(base_id),
                            datatable(base_id),
                        ],
                    )
                ],
            ),
            dcc.Interval(
                id="load_interval",
                n_intervals=0,
                max_intervals=0,  # <-- only run once
                interval=1,
            ),
            dcc.Store(id="intermediate-value"),
        ],
    )


final = pd.read_csv(
    '/Users/jtrimble/working/agbiome-dot-cloud-dashboards/dashbrd_ecosystem/app/all_data.csv'
    #"/home/emerson/Code/snthesis/agbiome/dashboards/"
    #"agbiome-dot-cloud-dashboards/dashbrd_ecosystem/"
    #"all_data.csv"
)

aims = (
    final.groupby(["threshold", "cluster"])["aim_number"]
    .nunique()
    .reset_index()
)

f = (
    final.loc[
        (final["psol_hypothesis_1"].notnull())
        & (final["psol_global_hypothesis"].notnull())
    ]
    .groupby("aim_number")
    .first()
    .reset_index()
    .head(100)
)

DROP_VALUES = {
    "GPA": "actual_percent_dead_gpa",
    "Leps": "actual_positive_percent_lep",
    "P-Sol": "psol_value",
}


def callbacks(app):
    @app.callback(
        Output("intermediate-value", "data"),
        Input("biologicals-visualize-bar-graph", "clickData"),
    )
    def clean_data(clickData=DEFAULT_CLUSTER_SIZE):
        return clickData

    @app.callback(
        Output("biologicals-visualize-datatable", "data"),
        [
            Input("biologicals-visualize-cluster-plot", "clickData"),
            Input("biologicals-visualize-bar-graph", "clickData"),
            Input("intermediate-value", "data"),
            Input(
                "biologicals-visualize-cluster-plot",
                "selectedData",
            ),
        ],
    )
    def cluster_info(click_data, bar_click, data, selected_clusters):
        button_id = ctx.triggered_id
        if click_data is None and bar_click is None:
            f = final.loc[final["threshold"] == DEFAULT_CLUSTER_SIZE]
        elif click_data is not None and bar_click is None:
            f = final.loc[final["threshold"] == DEFAULT_CLUSTER_SIZE]

        elif button_id == "cluster-plot" and bar_click is not None:
            f = final.loc[
                (final["threshold"] == click_data["points"][0]["label"])
                & (final["cluster"] == click_data["points"][0]["x"])
            ]
        elif button_id == "bar-graph" and click_data is not None:
            f = final.loc[final["threshold"] == bar_click["points"][0]["x"]]
        elif button_id == "bar-graph":
            f = final.loc[final["threshold"] == bar_click["points"][0]["x"]]
        else:
            f = final.loc[final["threshold"] == DEFAULT_CLUSTER_SIZE]
        df = f
        if selected_clusters is not None:
            d = final.iloc[
                [s["pointNumber"] for s in selected_clusters["points"]]
            ]
            clusters = d["cluster"].unique()
            df = f[f["cluster"].isin(clusters)]
        return df.to_dict(orient="records")

    @app.callback(
        [
            Output("slider", "max"),
            Output("slider", "marks"),
            Output("slider", "value"),
            Output("slider", "step"),
        ],
        Input("biologicals-visualize-assay-selector", "value"),
    )
    def update_slider(selected_item):
        if selected_item is None:
            return 5, {str(i): str(i) for i in range(0, 6)}, 2.5, 0.05
        elif selected_item in {"GPA", "Leps"}:
            return (
                1,
                {("0." + str(i)): str(i) for i in range(0, 10)},
                0.5,
                0.01,
            )
        else:
            return 15, {str(i): str(i) for i in range(0, 15)}, 5, 0.05

    @app.callback(
        Output("hypothesis-dropdown", "options"),
        Input("biologicals-visualize-assay-selector", "value"),
    )
    def dropdown_sorter(dropdown):
        if dropdown is None:
            return dash.no_update

        elif dropdown == "P-Sol":
            return ["psol_hypothesis_1", "psol_global_hypothesis"]
        elif dropdown == "GPA":
            return ["gpa_hypothesis_1", "gpa_global_hypothesis"]
        elif dropdown == "Leps":
            return ["lep_hypothesis_1", "lep_global_hypothesis"]

    @app.callback(
        Output("biologicals-visualize-parity-plot", "figure"),
        [
            Input(
                "biologicals-visualize-cluster-plot",
                "selectedData",
            ),
            Input("hypothesis-dropdown", "value"),
        ],
    )
    def make_parity_plot(selected, list_of_hypotheses):
        if list_of_hypotheses is None or len(list_of_hypotheses) == 0:
            return {"data": []}
        elif len(list_of_hypotheses) == 1:
            h1 = list_of_hypotheses[0]
            data = (
                final.loc[(final[h1].notnull())]
                .groupby("aim_number")
                .first()
                .reset_index()
            )

            return {
                "layout": {
                    "xaxis": {
                        "title": f"Activity Predictions for Hypothesis: {h1}"
                    },
                },
                "data": [
                    {
                        "x": "Activity Prediction",
                        "y": data[h1],
                        "name": "Activity Prediction",
                        "boxmean": "sd",
                        "type": "box",
                    }
                ],
            }
        else:
            if selected is None:
                selected = {"points": []}
            d = final.iloc[[s["pointNumber"] for s in selected["points"]]]
            clusters = d["cluster"].unique()
            h1 = list_of_hypotheses[0]
            h2 = list_of_hypotheses[1]
            f = (
                final.loc[(final[h1].notnull()) & (final[h2].notnull())]
                .groupby("aim_number")
                .first()
                .reset_index()
            )
            b = f[f["cluster"].isin(clusters)]

            return {
                "layout": {
                    "xaxis": {
                        "title": f"Activity Predictions for Hypothesis: {h1}"
                    },
                    "yaxis": {
                        "title": f"Activity Predictions for Hypothesis: {h2}"
                    },
                },
                "data": [
                    {
                        "type": "scattergl",
                        "y": f[h2],
                        "x": f[h1],
                        "name": "All AIMs",
                        "mode": "markers",
                    },
                    {
                        "type": "scattergl",
                        "y": b[h2],
                        "x": b[h1],
                        "mode": "markers",
                        "name": "selected clusters",
                        "marker": {
                            "color": "#dc8633",
                        },
                    },
                ],
            }

    @app.callback(
        Output("biologicals-visualize-cluster-plot", "figure"),
        Input(
            "biologicals-visualize-bar-graph",
            "clickData",
        ),
        Input("biologicals-visualize-assay-selector", "value"),
        Input("slider", "value"),
    )
    def distribution_figure(click_data, dropdown, slider):
        if click_data is None and dropdown is None:
            return dash.no_update
        elif dropdown is None and click_data is not None:
            return dash.no_update
        elif dropdown is not None and click_data is None:
            threshold = DEFAULT_CLUSTER_SIZE
        else:
            threshold = click_data["points"][0]["x"]

        avgs = (
            final.loc[final[DROP_VALUES[dropdown]].notnull()]
            .groupby(["threshold", "cluster"])[DROP_VALUES[dropdown]]
            .mean()
            .reset_index()
        )
        avgs = avgs.merge(aims, on=["threshold", "cluster"], how="left")
        avgs["log"] = (np.log(avgs["aim_number"]) + 1) * 10
        df = avgs.loc[avgs["threshold"] == threshold].sort_values(
            by="cluster", ascending=True
        )

        count = len(df[df[DROP_VALUES[dropdown]] > slider]["cluster"].unique())

        return {
            "layout": {
                "legend": {"orientation": "v", "y": 0.5, "x": 10000},
                "xaxis": {
                    "title": f"Cluster size at {round(threshold, 2)}% KID; {count} above threshold"
                },
                "yaxis": {
                    "title": f"Average Activity of Representatives in Cluster"
                },
            },
            "data": [
                {
                    "type": "scatter",
                    "y": df[DROP_VALUES[dropdown]],
                    "x": df.aim_number,
                    "mode": "markers",
                    "name": "Clusters",
                    # "marker": {
                    #      "color": df.log
                    #  }
                },
                {
                    "type": "line",
                    "y": [slider for i in df.aim_number],
                    "x": [str(i) for i in df.aim_number],
                    "mode": "line",
                    "name": "Activity Threshold",
                    "marker": {
                        "color": "red",
                    },
                },
            ],
        }

    @app.callback(
        Output("biologicals-visualize-bar-graph", "figure"),
        Input("biologicals-visualize-assay-selector", "value"),
        Input("slider", "value"),
    )
    def display_activity(drop_down_value, slider_value):
        if drop_down_value == None:
            cluster_data = (
                final.groupby("threshold")["cluster"].nunique().reset_index()
            )
            return {
                "layout": {
                    "barmode": "stack",
                    "xaxis": {"title": "Cluster Similarity Threshold"},
                    "yaxis": {"title": "Total Number of Clusters"},
                },
                "data": [
                    {
                        "type": "bar",
                        "x": cluster_data.threshold.values,
                        "y": cluster_data.cluster.values,
                        "marker": {
                            "color": "#236192",
                        },
                        "name": "all_clusters",
                        "base": 0,
                    },
                ],
            }

        else:
            df = final.loc[final[DROP_VALUES[drop_down_value]].notnull()]
            cluster_data = (
                df.groupby("threshold")["cluster"].nunique().reset_index()
            )
            avgs = (
                df.groupby(["threshold", "cluster"])[
                    DROP_VALUES[drop_down_value]
                ]
                .mean()
                .reset_index()
            )
            for threshold in set(avgs.threshold.tolist()):
                gt_threshold = (
                    avgs.loc[
                        avgs[DROP_VALUES[drop_down_value]] >= slider_value
                    ]
                    .groupby("threshold")["cluster"]
                    .nunique()
                    .reset_index()
                )
        return {
            "layout": {
                "barmode": "stack",
                "xaxis": {"title": "Cluster Similarity Threshold"},
                "yaxis": {"title": "Total Number of Clusters"},
            },
            "data": [
                {
                    "type": "bar",
                    "x": cluster_data.threshold.values,
                    "y": cluster_data.cluster.values,
                    "marker": {
                        "color": "#236192",
                    },
                    "name": "all_clusters",
                    "base": 0,
                },
                {
                    "type": "bar",
                    "x": gt_threshold.threshold.values,
                    "y": gt_threshold.cluster.values,
                    "marker": {
                        "color": "#dc8633",
                    },
                    "name": "cluster_avg_is_predicted_hit",
                    "base": 0,
                },
            ],
        }

    @app.callback(
        Output("biologicals-visualize-assay-selector", "options"),
        Input("biologicals-project-selector", "value"),
        prevent_initial_call=True,
    )
    def populate_assay_selection(project: str):
        print("HERE!!!!!!!!!!!!!!!!!!!!!!11")


def selection(base_id: str):
    dm = data.DataManager()

    assays = dm.assays()

    return dbc.Row(
        children=[
            dbc.Col(
                util.selection(
                    values=assays,
                    selector_id=f"{base_id}-assay-selector",
                    label="Select Assays to View",
                    # multi=True
                    value=assays[0],
                ),
                width=6,
            ),
            dbc.Col(
                util.selection(
                    values=["Assay Date", "Hypothesis", "Specific Subjects"],
                    selector_id=f"{base_id}-filter-selection",
                    label="Filter by Criteria",
                ),
                width=6,
            ),
        ],
    )


def graphs(base_id: str):
    return html.Div(
        children=[
            dbc.Row(
                children=[
                    dbc.Col(
                        width=6,
                        children=[
                            dcc.Graph(
                                id=f"{base_id}-bar-graph",
                            ),
                            html.Div("Activity Threshold"),
                            dcc.Slider(
                                id="slider",
                                step=0.05,
                                value=1,
                                min=0,
                            ),
                        ],
                    ),
                    dbc.Col(
                        width=6,
                        children=[
                            dcc.Graph(
                                id=f"{base_id}-cluster-plot",
                            ),
                            dbc.Row(
                                children=[
                                    dbc.Col(
                                        children=[
                                            dcc.Dropdown(
                                                id="hypothesis-dropdown",
                                                multi=True,
                                                placeholder="Select associated assay hypotheses to view. Maximum 2",
                                            ),
                                        ]
                                    ),
                                    dbc.Col(
                                        children=[
                                            dbc.Button(
                                                "Clear Cluster Selection",
                                                id="clear-cluster-selection",
                                                className="float-end",
                                                color="danger",
                                                outline=True,
                                            ),
                                        ]
                                    ),
                                ]
                            ),
                        ],
                    ),
                ],
            ),
            dbc.Row(
                children=[
                    dbc.Col(
                        dcc.Graph(
                            id=f"{base_id}-graph-c",
                            figure=go.Figure(
                                data=[go.Scatter(x=[1, 2, 3], y=[4, 1, 2])],
                            ),
                        ),
                        width=6,
                    ),
                    dbc.Col(
                        dcc.Graph(
                            id=f"{base_id}-parity-plot",
                        ),
                        width=6,
                    ),
                ],
            ),
        ],
    )


def datatable(base_id: str):
    columns = [
        {
            "name": "AIM",
            "id": "aim_number",
            "hideable": False,
        },
        {
            "name": "Cluster",
            "id": "cluster",
            "hideable": True,
        },
        {
            "name": "Threshold",
            "id": "threshold",
            "hideable": True,
        },
        {
            "name": "GPA Predicted Death",
            "id": "gpa_predicted_death",
            "hideable": True,
        },
        {
            "name": "Actual % Dead GPA",
            "id": "actual_percent_dead_gpa",
            "hideable": True,
        },
        {
            "name": "Leps Predicted Death",
            "id": "leps_predicted_death",
            "hideable": True,
        },
        {
            "name": "Actual Positive % Lep",
            "id": "actual_positive_percent_lep",
            "hideable": True,
        },
        {
            "name": "psol_hypothesis_1",
            "id": "psol_hypothesis_1",
            "hideable": True,
        },
        {
            "name": "psol_global_hypothesis",
            "id": "psol_global_hypothesis",
            "hideable": True,
        },
        {
            "name": "psol_value",
            "id": "psol_value",
            "hideable": True,
        },
    ]

    return dbc.Row(
        dbc.Col(
            children=[
                dash_table.DataTable(
                    id=f"{base_id}-datatable",
                    columns=columns,
                    merge_duplicate_headers=True,
                    markdown_options={"html": True},
                    editable=False,
                    row_deletable=False,
                    persistence_type="memory",
                    page_current=0,
                    page_size=constants.LARGE_DATATABLE_SIZE,
                    style_table={
                        "overflowX": "auto",
                        "paddingRight": "1px",
                        "minWidth": "100%",
                        "minHeight": 800,
                        "height": 800,
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
                dbc.Button(
                    "Add selected to working set",
                    id="add-visualize-to-working-set",
                    className="float-end",
                    color="primary",
                ),
            ],
        ),
    )

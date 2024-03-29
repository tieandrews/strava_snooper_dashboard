import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import dash_loading_spinners
import pandas as pd
import time
import sys
import os

src_path = os.path.abspath(os.path.join(".."))
if src_path not in sys.path:
    sys.path.append(src_path)

from app import app
from src.pages.layouts import header, footer, blank_placeholder_plot
from src.visualizations.kudos_prediction_dash_plots import (
    plot_predicted_kudos_value,
    plot_distance_prediction,
    plot_elevation_prediction,
    plot_achievement_prediction,
    plot_prediction_vs_actual_data,
)
from src.data.kudos_data_load import load_static_kudos_predictions
from src.data.gcp_strava_data_load_preprocess import load_strava_activity_data_from_bq
from src.models.predict_kudos import predict_kudos

# initial values
num_followers = 100
distance = 60  # km
custom_name_bool = 0
achievements = 15
elevation = 4  # 100's of meters

loading_speed_multiplier = 1.5
loading_color = "#e95420"
loading_width = 125

# date of raw data file to load
raw_kudos_data_date = "2022-05-18"

kudos_controls = html.Div(
    [
        html.P(
            "Pick what your ride will look like and this will predict how many kudos you'll get."
        ),
        html.P("How Many Followers you have:"),
        dbc.Input(
            type="number", min=5, max=1000, step=1, value=100, id="num-followers"
        ),
        html.Br(),
        dbc.Col(
            [
                dbc.Label("Ride Naming"),
                dbc.RadioItems(
                    options=[
                        {"label": "Standard Ride Name", "value": 0},
                        {"label": "Custom Ride Name", "value": 1},
                    ],
                    value=custom_name_bool,
                    id="custom-name-input",
                    inline=True,
                    style={"text-align": "center"},
                ),
                html.Br(),
                dbc.Label("Ride Distance (km)"),
                dcc.Slider(
                    min=20,
                    max=230,
                    step=10,
                    value=distance,
                    id="distance-slider",
                    marks={int(i): str(i) for i in range(20, 240, 10)},
                ),
                html.Br(),
                dbc.Label("Elevation Gain (hundreds of m)"),
                dcc.Slider(
                    min=2,
                    max=29,
                    step=1,
                    value=elevation,
                    id="elevation-slider",
                    marks={int(i): str(i) for i in range(0, 31, 1)},
                ),
                html.Br(),
                dbc.Label("Strava Achievements on Ride"),
                dcc.Slider(
                    min=0,
                    max=50,
                    step=5,
                    value=achievements,
                    id="achievements-slider",
                    marks={int(i): str(i) for i in range(0, 55, 5)},
                ),
                html.Br(),
            ],
        ),
    ],
)

# DCC card for showing my activitees over time etc.
kudos_prediction_card = dbc.Card(
    [
        dbc.CardHeader(html.H4("How Many Kudos Will You Get on Your Next Ride?")),
        dbc.CardBody(
            children=[
                dbc.Row(
                    [
                        dbc.Col(kudos_controls, width=12, lg=7),
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody(
                                    children=[
                                        dash_loading_spinners.Ring(
                                            children=[
                                                dcc.Graph(
                                                    id="kudos-plot",
                                                    figure=blank_placeholder_plot(),
                                                    config={"displayModeBar": False},
                                                )
                                            ],
                                            speed_multiplier=loading_speed_multiplier,
                                            width=loading_width,
                                            color=loading_color,
                                        ),
                                    ]
                                )
                            ),
                            width=12,
                            lg=5,
                        ),
                    ]
                ),
                dbc.Row(
                    html.H5(
                        "Use these to Maximize your Kudos",
                        style={"textAlign": "center"},
                    ),
                    justify="center",
                ),
                dbc.Row(
                    dbc.Col(
                        [
                            dbc.CardGroup(
                                [
                                    dbc.Card(
                                        dbc.CardBody(
                                            children=[
                                                dash_loading_spinners.Ring(
                                                    children=[
                                                        dcc.Graph(
                                                            id="dist-plot",
                                                            figure=blank_placeholder_plot(),
                                                            config={
                                                                "displayModeBar": False
                                                            },
                                                        )
                                                    ],
                                                    speed_multiplier=loading_speed_multiplier,
                                                    width=loading_width,
                                                    color=loading_color,
                                                ),
                                            ]
                                        ),
                                    ),
                                    dbc.Card(
                                        dbc.CardBody(
                                            children=[
                                                dash_loading_spinners.Ring(
                                                    children=[
                                                        dcc.Graph(
                                                            id="elev-plot",
                                                            figure=blank_placeholder_plot(),
                                                            config={
                                                                "displayModeBar": False
                                                            },
                                                        )
                                                    ],
                                                    speed_multiplier=loading_speed_multiplier,
                                                    width=loading_width,
                                                    color=loading_color,
                                                ),
                                            ]
                                        )
                                    ),
                                    dbc.Card(
                                        dbc.CardBody(
                                            children=[
                                                dash_loading_spinners.Ring(
                                                    children=[
                                                        dcc.Graph(
                                                            id="achiev-plot",
                                                            figure=blank_placeholder_plot(),
                                                            config={
                                                                "displayModeBar": False
                                                            },
                                                        )
                                                    ],
                                                    speed_multiplier=loading_speed_multiplier,
                                                    width=loading_width,
                                                    color=loading_color,
                                                ),
                                            ]
                                        )
                                    ),
                                ]
                            ),
                        ],
                        width=12,
                    )
                ),
            ]
        ),
    ],
    color="#E0E0E0",
)

layout = html.Div(
    [
        header(),
        dbc.Row(
            dbc.Col(
                kudos_prediction_card,
                width={"size": 12, "offset": 0},
                lg={"size": 10, "offset": 1},
            )
        ),
        footer(),
        html.Div(id="kudos-page-load-div"),
        dcc.Store(id="kudos-static-data", data=None, storage_type="session"),
    ]
)


@app.callback(
    Output(component_id="kudos-plot", component_property="figure"),
    Output(component_id="dist-plot", component_property="figure"),
    Output(component_id="elev-plot", component_property="figure"),
    Output(component_id="achiev-plot", component_property="figure"),
    Output("kudos-static-data", "data"),
    [
        Input(component_id="num-followers", component_property="value"),
        Input(component_id="custom-name-input", component_property="value"),
        Input(component_id="distance-slider", component_property="value"),
        Input(component_id="elevation-slider", component_property="value"),
        Input(component_id="achievements-slider", component_property="value"),
        Input("kudos-page-load-div", "children"),
    ],
    State("kudos-static-data", "kudos_static_dict"),
)
def update_predicted_kudos_number(
    num_followers,
    custom_name_bool,
    distance,
    elevation,
    achievements,
    _children,
    kudos_static_dict,
):
    """Accepts changed features for predicting kudos and shows updated predicted kudos numbers along
    with the optimization plots where max kudos can be gained.

    Args:
        num_followers (int): How many followers the user entered.
        custom_name_bool (int): 0 for standard name, 1 for custom name
        distance (int): distance in kilometers
        elevation (int): elevation gain in meters
        achievements (int): no. of achievements gained on the activity
        _children (None): Placeholder for a div to trigger on page load instead of interaction.
        kudos_static_dict (dict): the cached static kudos prediction data for fast reloading.

    Returns:
        figures: multiple figures are returned with updated data etc.
        dict (dcc.Store): the updated cached data is returned so further interactions don't trigger a reload of the data.
    """

    if kudos_static_dict is None:
        static_kudos_predictions = load_static_kudos_predictions(raw_kudos_data_date)
        kudos_static_dict = static_kudos_predictions.to_dict("records")
    else:
        static_kudos_predictions = pd.DataFrame(kudos_static_dict)

    elevation_m = elevation * 100  # get into meters

    perc_followers = static_kudos_predictions.loc[
        (static_kudos_predictions.distance == distance)
        & (static_kudos_predictions.achievements == achievements)
        & (static_kudos_predictions.elevation == elevation_m)
        & (static_kudos_predictions.custom_name_bool == custom_name_bool),
        "kudos_prediction",
    ]

    kudos_prediction = perc_followers.iloc[0] * num_followers

    kudos_value_fig = plot_predicted_kudos_value(round(kudos_prediction))
    distance_value_fig = plot_distance_prediction(
        static_kudos_predictions,
        kudos_prediction,
        num_followers,
        custom_name_bool,
        distance,
        elevation_m,
        achievements,
    )

    elevation_value_fig = plot_elevation_prediction(
        static_kudos_predictions,
        kudos_prediction,
        num_followers,
        custom_name_bool,
        distance,
        elevation_m,
        achievements,
    )

    achievement_value_fig = plot_achievement_prediction(
        static_kudos_predictions,
        kudos_prediction,
        num_followers,
        custom_name_bool,
        distance,
        elevation_m,
        achievements,
    )

    return (
        kudos_value_fig,
        distance_value_fig,
        elevation_value_fig,
        achievement_value_fig,
        kudos_static_dict,
    )

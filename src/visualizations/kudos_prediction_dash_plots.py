import os
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import json
from sklearn.metrics import accuracy_score

from src.data.kudos_data_load import load_static_kudos_predictions

ORANGE = "#FFA400"
BLUE = "#009FFD"


def plot_predicted_kudos_value(kudos):
    """Visualizes a simple text and number of how many kudos were predicted.

    Args:
        kudos (int): No. of kudos

    Returns:
        go.Figure: THe standalone figure with Predicted kudos and the number displayed.
    """

    fig = go.Figure(
        go.Indicator(
            mode="number",
            value=kudos,
            title={"text": "Predicted <br>Kudos"},
            number={"font": {"size": 135}},
            # number={"suffix": " kudos"},
            # delta = {'position': "top", 'reference': 320},
            domain={"x": [0, 1], "y": [0, 1]},
        )
    )

    return fig


def plot_distance_prediction(
    kudos_pred_df,
    kudos_prediction,
    num_followers,
    custom_name_bool,
    distance,
    elevation,
    achievements,
):
    """Builds a figure showing the effect of DISTANCE on kudos predictions, including
    the point at which DISTANCE kudos are maximized and where the current inputs fall
    on the curve.

    Args:
        kudos_pred_df (DataFrame): The pre-generated kudos predcitions dataframe
        kudos_prediction (float): How many kudos are predicted.
        num_followers (int): No. of followers selected.
        custom_name_bool (int): 0 for stanfard ride name, 1 for custom ride name
        distance (int): ride distance in km's
        elevation (int): elevation gain on the ride in meters
        achievements (int): No. of achievements

    Returns:
        px.line: The final line plot with predicted curve, max and current kudos labelled
    """

    dist_plot = px.line(
        x=kudos_pred_df.loc[
            (kudos_pred_df.achievements == achievements)
            & (kudos_pred_df.elevation == elevation)
            & (kudos_pred_df.custom_name_bool == custom_name_bool),
            "distance",
        ],
        y=kudos_pred_df.loc[
            (kudos_pred_df.achievements == achievements)
            & (kudos_pred_df.elevation == elevation)
            & (kudos_pred_df.custom_name_bool == custom_name_bool),
            "kudos_prediction",
        ]
        * num_followers,
        labels=dict(x="<b>Distance</b> (km)", y="Predicted Kudos"),
        color_discrete_sequence=[ORANGE],
    )

    dist_plot.add_trace(
        go.Scatter(
            x=[distance],
            y=[kudos_prediction],
            mode="markers",
            name="Prediction",
            marker=dict(color=BLUE, size=14, line=dict(width=0)),
        )
    )

    max_perc_kudos = kudos_pred_df.loc[
        (kudos_pred_df.elevation == elevation)
        & (kudos_pred_df.achievements == achievements)
        & (kudos_pred_df.custom_name_bool == custom_name_bool),
        "kudos_prediction",
    ].max()
    min_val = kudos_pred_df.loc[
        (kudos_pred_df.elevation == elevation)
        & (kudos_pred_df.achievements == achievements)
        & (kudos_pred_df.custom_name_bool == custom_name_bool)
        & (kudos_pred_df.kudos_prediction == max_perc_kudos),
        "distance",
    ].min()

    dist_plot.add_trace(
        go.Scatter(
            x=[min_val],
            y=[max_perc_kudos * num_followers],
            mode="markers",
            name="Max Kudos",
            marker=dict(color="lime", size=8),
        )
    )

    dist_plot.update_layout(
        title=f"<b>Kudos</b> vs. <b>Distance</b>",
        title_x=0.5,
        title_font_size=15,
        font_size=10,
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(
            # orientation="h",
            yanchor="bottom",
            y=0,
            xanchor="right",
            x=1.0,
        ),
    )

    return dist_plot


def plot_elevation_prediction(
    kudos_pred_df,
    kudos_prediction,
    num_followers,
    custom_name_bool,
    distance,
    elevation,
    achievements,
):
    """Builds a figure showing the effect of ELEAVTION GAIN on kudos predictions, including
    the point at which ELEVATION GAIN kudos are maximized and where the current inputs fall
    on the curve.

    Args:
        kudos_pred_df (DataFrame): The pre-generated kudos predcitions dataframe
        kudos_prediction (float): How many kudos are predicted.
        num_followers (int): No. of followers selected.
        custom_name_bool (int): 0 for stanfard ride name, 1 for custom ride name
        distance (int): ride distance in km's
        elevation (int): elevation gain on the ride in meters
        achievements (int): No. of achievements

    Returns:
        px.line: The final line plot with predicted curve, max and current kudos labelled
    """

    elevation_plot = px.line(
        x=kudos_pred_df.loc[
            (kudos_pred_df.achievements == achievements)
            & (kudos_pred_df.distance == distance)
            & (kudos_pred_df.custom_name_bool == custom_name_bool),
            "elevation",
        ],
        y=kudos_pred_df.loc[
            (kudos_pred_df.achievements == achievements)
            & (kudos_pred_df.distance == distance)
            & (kudos_pred_df.custom_name_bool == custom_name_bool),
            "kudos_prediction",
        ]
        * num_followers,
        labels=dict(x="<b>Elevation Gain</b> (m)", y="Predicted Kudos"),
        color_discrete_sequence=[ORANGE],
    )

    elevation_plot.add_trace(
        go.Scatter(
            x=[elevation],
            y=[kudos_prediction],
            mode="markers",
            name="Prediction",
            marker=dict(color=BLUE, size=14, line=dict(width=0)),
        )
    )

    max_perc_kudos = kudos_pred_df.loc[
        (kudos_pred_df.achievements == achievements)
        & (kudos_pred_df.distance == distance)
        & (kudos_pred_df.custom_name_bool == custom_name_bool),
        "kudos_prediction",
    ].max()
    min_val = kudos_pred_df.loc[
        (kudos_pred_df.achievements == achievements)
        & (kudos_pred_df.distance == distance)
        & (kudos_pred_df.custom_name_bool == custom_name_bool)
        & (kudos_pred_df.kudos_prediction == max_perc_kudos),
        "elevation",
    ].min()

    elevation_plot.add_trace(
        go.Scatter(
            x=[min_val],
            y=[max_perc_kudos * num_followers],
            mode="markers",
            name="Max Kudos",
            marker=dict(color="lime", size=8),
        )
    )

    elevation_plot.update_layout(
        title=f"<b>Kudos</b> vs. <b>Elevation</b>",
        title_x=0.5,
        title_font_size=15,
        font_size=10,
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(
            # orientation="h",
            yanchor="bottom",
            y=0,
            xanchor="right",
            x=1.0,
        ),
    )

    return elevation_plot


def plot_achievement_prediction(
    kudos_pred_df,
    kudos_prediction,
    num_followers,
    custom_name_bool,
    distance,
    elevation,
    achievements,
):
    """Builds a figure showing the effect of ACHIEVEMENT COUNT on kudos predictions, including
    the point at which ACHIEVEMENT COUNT kudos are maximized and where the current inputs fall
    on the curve.

    Args:
        kudos_pred_df (DataFrame): The pre-generated kudos predcitions dataframe
        kudos_prediction (float): How many kudos are predicted.
        num_followers (int): No. of followers selected.
        custom_name_bool (int): 0 for stanfard ride name, 1 for custom ride name
        distance (int): ride distance in km's
        elevation (int): elevation gain on the ride in meters
        achievements (int): No. of achievements

    Returns:
        px.line: The final line plot with predicted curve, max and current kudos labelled
    """

    achievement_plot = px.line(
        x=kudos_pred_df.loc[
            (kudos_pred_df.elevation == elevation)
            & (kudos_pred_df.distance == distance)
            & (kudos_pred_df.custom_name_bool == custom_name_bool),
            "achievements",
        ],
        y=kudos_pred_df.loc[
            (kudos_pred_df.elevation == elevation)
            & (kudos_pred_df.distance == distance)
            & (kudos_pred_df.custom_name_bool == custom_name_bool),
            "kudos_prediction",
        ]
        * num_followers,
        labels=dict(x="<b>Achievements</b>", y="Predicted Kudos"),
        color_discrete_sequence=[ORANGE],
    )

    achievement_plot.add_trace(
        go.Scatter(
            x=[achievements],
            y=[kudos_prediction],
            mode="markers",
            name="Prediction",
            marker=dict(color=BLUE, size=14, line=dict(width=0)),
        )
    )

    max_perc_kudos = kudos_pred_df.loc[
        (kudos_pred_df.elevation == elevation)
        & (kudos_pred_df.distance == distance)
        & (kudos_pred_df.custom_name_bool == custom_name_bool),
        "kudos_prediction",
    ].max()
    min_val = kudos_pred_df.loc[
        (kudos_pred_df.elevation == elevation)
        & (kudos_pred_df.distance == distance)
        & (kudos_pred_df.custom_name_bool == custom_name_bool)
        & (kudos_pred_df.kudos_prediction == max_perc_kudos),
        "achievements",
    ].min()

    achievement_plot.add_trace(
        go.Scatter(
            x=[min_val],
            y=[max_perc_kudos * num_followers],
            mode="markers",
            name="Max Kudos",
            marker=dict(color="lime", size=8),
        )
    )

    achievement_plot.update_layout(
        title=f"<b>Kudos</b> vs. <b>Achievements</b>",
        title_x=0.5,
        title_font_size=15,
        font_size=10,
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(
            # orientation="h",
            yanchor="bottom",
            y=0,
            xanchor="right",
            x=1.0,
        ),
    )

    return achievement_plot


def plot_prediction_vs_actual_data(actual_kudos, pred_kudos):
    """Displays a cross plot of data points of predicted vs. actual number of kudos for monitoring
    the model.

    Args:
        actual_kudos (list): Actual kudos count from Strava
        pred_kudos (list): predcited kudos count from the model

    Returns:
        px.scatter: Plotly express scatter plot with diagonal line indicating "ideal" performance of the model
                    for simpelr interpretation.
    """

    x_min, x_max = (0, max(actual_kudos + pred_kudos) + 2)
    y_min, y_max = (0, max(actual_kudos + pred_kudos) + 2)

    kudo_pred_plot = px.scatter(
        x=actual_kudos, y=pred_kudos, color_discrete_sequence=["#FFA400"]
    ).update_traces(marker=dict(size=10, line_width=2, line_color="black"))

    kudo_pred_plot.update_layout(
        title=f"Predicted vs. Actual Kudos<br>of Most Recent {len(actual_kudos)} Rides",
        xaxis=dict(
            title="ACTUAL No. of Kudos",
            # tickformat=",.0%",
            range=[x_min, x_max],
        ),
        yaxis=dict(
            title="PREDICTED No. of Kudos",
            # tickformat=",.0%",
            range=[y_min, y_max],
        ),
        title_x=0.5,
        title_font_size=17,
        font_size=12,
        margin=dict(l=5, r=5, t=50, b=20),
        legend=dict(
            # orientation="h",
            yanchor="top",
            y=1.0,
            xanchor="right",
            x=1,
        ),
        shapes=[
            {
                "type": "line",
                "yref": "paper",
                "xref": "paper",
                "y0": 0,
                "y1": 1,
                "x0": 0,
                "x1": 1,
                "layer": "below",
            }
        ],
    )

    kudo_pred_plot.add_annotation(
        text="Ideal Predictions",
        xref="paper",
        yref="paper",
        x=0.9,
        y=1.0,
        showarrow=False,
        font=dict(
            size=16,
        ),
    )

    return kudo_pred_plot

# Provides a plotly figure for showing UK temperatures as a contour plot

import plotly.graph_objects as go
import numpy as np


def UKTC_Figure(dataCube):

    fig = go.Figure(
        data=go.Contour(
            z=dataCube.data,
            colorscale="RdBu",
            reversescale=True,
            zmin=-5,
            zmax=15,
            ncontours=100,
            line=go.contour.Line(width=0),
            x=dataCube.coord("projection_x_coordinate").points / 1000,
            y=dataCube.coord("projection_y_coordinate").points / 1000,
        )
    )
    fig.update_layout(
        autosize=False,
        width=548,
        height=704,
        margin=dict(l=50, r=50, b=100, t=100, pad=4),
        paper_bgcolor="LightSteelBlue",
        title_text="Tmax from UKPP (C)",
    )
    return fig

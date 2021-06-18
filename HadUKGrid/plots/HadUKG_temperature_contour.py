# Provides a plotly figure for showing UK temperatures as a contour plot

import plotly.graph_objects as go
import numpy as np


def HUKG_Figure(dataCube):

    fig = go.Figure(
        data=go.Contour(
            z=dataCube.data.data, colorscale="RdBu", reversescale=True, zmin=-5, zmax=15
        )
    )
    fig.update_layout(
        autosize=False,
        width=548,
        height=704,
        margin=dict(l=50, r=50, b=100, t=100, pad=4),
        paper_bgcolor="LightSteelBlue",
    )
    return fig

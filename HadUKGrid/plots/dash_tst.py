#!/usr/bin/env python

import os
import sys
import iris
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html

sys.path.append("%s/." % os.path.dirname(__file__))
from UKPP_load_temperature import UKPP_load_tasmax
from temperature_contour import Tmax_Figure
from HUKG_load_tmax import HUKG_load_tmax
from HUKG_load_tmax import HUKG_load_tmax_climatology

state = {
    "year": 2021,
    "month": 3,
    "day": 28,
    "type": "anomalies",
    "actuals": {
        "zmin": -5,
        "zmax": 15,
    },
    "anomalies": {
        "zmin": -5,
        "zmax": 5,
    },
    "xmin": -200,
    "xmax": 700,
    "ymin": -200,
    "ymax": 1250,
}

cdata = HUKG_load_tmax_climatology(state["year"], state["month"], state["day"])
hdata = UKPP_load_tasmax(state["year"], state["month"], state["day"])
cfig = Tmax_Figure(
    hdata - cdata,
    title="Tmax from UKPP",
    zmin=state[state["type"]]["zmin"],
    zmax=state[state["type"]]["zmax"],
)
ddata = HUKG_load_tmax(state["year"], state["month"], state["day"])
dfig = Tmax_Figure(
    ddata - cdata,
    title="Tmax from HadUKGrid",
    zmin=state[state["type"]]["zmin"],
    zmax=state[state["type"]]["zmax"],
)

app = dash.Dash()
app.layout = html.Div(
    [
        html.H1(
            "%04d-%02d-%02d %s"
            % (state["year"], state["month"], state["day"], state["type"])
        ),
        dcc.Graph(figure=dfig, style={"display": "inline-block"}),
        dcc.Graph(figure=cfig, style={"display": "inline-block"}),
    ],
    style={"padding": 10},
)
if __name__ == "__main__":
    app.run_server(debug=True, port=8000, host="0.0.0.0")

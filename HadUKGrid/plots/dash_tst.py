#!/usr/bin/env python

import os
import sys
import iris
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html

sys.path.append("%s/." % os.path.dirname(__file__))
from UKPP_load_temperature import UKPP_load_hourly
from UK_temperature_contour import UKTC_Figure
from HUKG_load_tmax import HUKG_load_tmax
from HadUKG_temperature_contour import HUKG_Figure

hdata = UKPP_load_hourly(2021, 3, 12, 22)
cfig = UKTC_Figure(hdata)
ddata = HUKG_load_tmax(2021, 3, 12)
dfig = HUKG_Figure(ddata)

app = dash.Dash()
app.layout = html.Div(
    [
        dcc.Graph(figure=cfig, style={"display": "inline-block"}),
        dcc.Graph(figure=dfig, style={"display": "inline-block"}),
    ]
)
if __name__ == "__main__":
    app.run_server(debug=True, port=8000, host="0.0.0.0")

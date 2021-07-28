#!/usr/bin/env python

# Box-and-whisker time series of UK Tmax
#  Compared haduk-grid and Improver

import os
import sys
import numpy as np
import datetime
import copy

import iris
import iris.analysis

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

sys.path.append("%s/../../../utils/plots" % os.path.dirname(__file__))
from HUKG_load_tmax import HUKG_load_tmax
from HUKG_load_tmax import HUKG_load_tmax_climatology

sys.path.append("%s/." % os.path.dirname(__file__))
from Improver_load_tmax import Improver_load_tmax
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--year", help="Year", type=int, required=True)
parser.add_argument("--month", help="Integer month", type=int, required=True)
parser.add_argument("--day", help="Day of month", type=int, required=True)
parser.add_argument(
    "--lead_time", help="Forecast lead (hours)", type=int, required=False, default=0
)
parser.add_argument(
    "--adjustment", help="Adjustment method", type=str, required=False, default="raw"
)
parser.add_argument(
    "--dayrange", help="No. of days each side", type=int, required=False, default=7
)
parser.add_argument(
    "--opdir", help="Directory for output files", default=None, type=str, required=False
)
parser.add_argument(
    "--type",
    help="actuals, anomalies, or differences",
    choices=["actuals", "anomalies", "differences"],
    type=str,
    required=True,
)
parser.add_argument(
    "--latMax", help="Max. latitude to plot", type=int, required=False, default=1250
)
parser.add_argument(
    "--latMin", help="Min. latitude to plot", type=int, required=False, default=-200
)
parser.add_argument(
    "--lonMax", help="Max. longitude to plot", type=int, required=False, default=700
)
parser.add_argument(
    "--lonMin", help="Min. longitude to plot", type=int, required=False, default=-200
)
parser.add_argument(
    "--vMax", help="Max. temperature in scale", type=float, required=False, default=None
)
parser.add_argument(
    "--vMin", help="Min. temperature in scale", type=float, required=False, default=None
)
args = parser.parse_args()

opdir = None
if args.opdir is None:
    opdir = (
        "%s/Proxy_Hadobs/figures/haduk-grid/Improver/daily-maxtemp/%s/%04d/%02d/%02d"
        % (
            os.getenv("SCRATCH"),
            args.adjustment,
            args.year,
            args.month,
            args.day,
        )
    )
else:
    opdir = args.opdir

if not os.path.isdir(opdir):
    os.makedirs(opdir)


def loadDaily(args):
    # Load the source data
    if args.source == "HadUKGrid":
        sdata = HUKG_load_tmax(args)
    elif args.source == "Improver":
        sdata = Improver_load_tmax(args)

    # Subtract the climatology, if anomalies wanted
    if args.type == "anomalies":
        cdata = HUKG_load_tmax_climatology(args)
        cdata = cdata.regrid(sdata, iris.analysis.Nearest())
        sdata = sdata - cdata

    # Subtract the other source, if differences wanted
    if args.type == "differences":
        if args.source == "Improver":
            ddata = HUKG_load_tmax(args)
        elif args.source == "HadUKGrid":
            ddata = Improver_load_tmax(args)
        ddata = ddata.regrid(sdata, iris.analysis.Nearest())
        sdata = sdata - ddata

    return sdata


# Boxplot for one day
def box_1_day(args, offset, ax):
    dte = datetime.date(args.year, args.month, args.day)
    current = dte + datetime.timedelta(days=offset)
    atmp = copy.deepcopy(args)
    atmp.year = current.year
    atmp.month = current.month
    atmp.day = current.day
    vMax = 0
    vMin = 0
    # HadCRUTGrid box
    atmp.source = "HadUKGrid"
    if atmp.type == "differences":
        atmp.type = "anomalies"
    bColour = (174 / 255, 199 / 255, 232 / 255)  # T10 blue light
    if offset == 0:
        bColour = (31 / 255, 119 / 255, 180 / 255)  # T10 blue
    try:
        cdata = loadDaily(atmp)
        vMax = np.max(cdata.data)
        vMin = np.min(cdata.data)
        ax.boxplot(
            cdata.data.compressed(),
            positions=[offset - 1 / 5],
            widths=1 / 4,
            whis=(0, 100),
            showcaps=False,
            medianprops={"color": "black"},
            whiskerprops={"color": bColour},
            boxprops={"facecolor": bColour},
            patch_artist=True,
        )
    except Exception as e:
        print(e)
        pass
    # forecast box
    atmp.source = "Improver"
    atmp.type = args.type
    bColour = (255 / 255, 152 / 255, 150 / 255)  # T10 red light
    if offset == 0:
        bColour = (214 / 255, 39 / 255, 40 / 255)  # T10 red
    try:
        cdata = loadDaily(atmp)
        vMax = max(vMax, np.max(cdata.data))
        vMin = min(vMin, np.min(cdata.data))
        ax.boxplot(
            cdata.data.compressed(),
            positions=[offset + 1 / 5],
            widths=1 / 4,
            whis=(0, 100),
            showcaps=False,
            medianprops={"color": "black"},
            whiskerprops={"color": bColour},
            boxprops={"facecolor": bColour},
            patch_artist=True,
        )
    except Exception as e:
        print(e)
        pass
    return (vMax, vMin)


fig = Figure(
    figsize=(22, 5),
    dpi=100,
    facecolor=(0.5, 0.5, 0.5, 1),
    edgecolor=None,
    linewidth=0.0,
    frameon=False,
    subplotpars=None,
    tight_layout=None,
)
canvas = FigureCanvas(fig)
font = {
    "family": "sans-serif",
    "sans-serif": "Arial",
    "weight": "normal",
    "size": 20,
}
matplotlib.rc("font", **font)
axb = fig.add_axes([0, 0, 1, 1])
ax_ts = fig.add_axes([0.03, 0.07, 0.96, 0.9])
ax_ts.set_ylim(-1, 1)
ax_ts.set_xlim(args.dayrange * -1 - 0.5, args.dayrange + 0.5)
ax_ts.set_aspect("auto")

ticL = []
ticV = []
vMax = 1
vMin = -1
dte = datetime.date(args.year, args.month, args.day)
for offset in range(args.dayrange * -1, args.dayrange + 1):
    (dMx, dMn) = box_1_day(args, offset, ax_ts)
    vMax = max(vMax, dMx)
    vMin = min(vMin, dMn)
    ticV.append(offset)
    current = dte + datetime.timedelta(days=offset)
    tL = "%02d" % current.day
    if offset == 0 or current.day == 1:
        tL = "%02d-%02d" % (current.month, current.day)
    ticL.append(tL)

# For anomalies and differences, mark the Zero line
if args.type == "anomalies" or args.type == "differences":
    ax_ts.add_line(
        Line2D(
            [args.dayrange * -1 - 0.5, args.dayrange + 0.5],
            [0, 0],
            linewidth=0.25,
            color=(0, 0, 0, 1),
            alpha=1.0,
            zorder=1,
        )
    )

if args.type == "anomalies" or args.type == "differences":
    vMax = max(vMax, vMin * -1)
    vMin = vMax * -1

if args.vMax is not None:
    vMax = args.vMax
if args.vMin is not None:
    vMin = args.vMin

ax_ts.set_ylim(vMin, vMax)

ax_ts.set_xticks(ticV)
ax_ts.set_xticklabels(ticL)

fig.savefig("%s/TS_%03d_%s.png" % (opdir, args.lead_time, args.type))

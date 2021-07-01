#!/usr/bin/env python

# Box-and-whisker time series of UK Tmax

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

sys.path.append("%s/./HUKG" % os.path.dirname(__file__))
from HUKG_load_tmax import HUKG_load_tmax
from HUKG_load_tmax import HUKG_load_tmax_climatology

sys.path.append("%s/./UKPP" % os.path.dirname(__file__))
from UKPP_load_tmax import UKPP_load_tmax
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--year", help="Year", type=int, required=True)
parser.add_argument("--month", help="Integer month", type=int, required=True)
parser.add_argument("--day", help="Day of month", type=int, required=True)
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
    opdir = "%s/Proxy_Hadobs/figures/HadUKGrid/daily/Tmax/%04d/%02d/%02d" % (
        os.getenv("SCRATCH"),
        args.year,
        args.month,
        args.day,
    )
else:
    opdir = args.opdir

if not os.path.isdir(opdir):
    os.makedirs(opdir)

if args.vMax is None:
    if args.type == "anomalies" or args.type == "differences":
        args.vMax = 10
    else:
        args.vMax = (10, 10, 12, 14, 16, 18, 20, 20, 18, 16, 14, 12)[args.month - 1]
if args.vMin is None:
    if args.type == "anomalies" or args.type == "differences":
        args.vMin = args.vMax * -1
    else:
        args.vMin = (-10, -10, -8, -6, -4, -2, 0, 0, -2, -4, -6, -8)[args.month - 1]


def loadDaily(args):
    # Load the source data
    if args.source == "HadUKGrid":
        sdata = HUKG_load_tmax(args)
    elif args.source == "UKPP":
        sdata = UKPP_load_tmax(args)

    # Subtract the climatology, if anomalies wanted
    if args.type == "anomalies":
        cdata = HUKG_load_tmax_climatology(args)
        cdata = cdata.regrid(sdata, iris.analysis.Nearest())
        sdata = sdata - cdata

    # Subtract the other source, if differences wanted
    if args.type == "differences":
        if args.source == "UKPP":
            ddata = HUKG_load_tmax(args)
        elif args.source == "HadUKGrid":
            ddata = UKPP_load_tmax(args)
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
    # HadCRUTGrid box
    atmp.source = "HadUKGrid"
    if atmp.type == "differences":
        atmp.type = "anomalies"
    bColour = (174 / 255, 199 / 255, 232 / 255)  # T10 blue light
    if offset == 0:
        bColour = (31 / 255, 119 / 255, 180 / 255)  # T10 blue
    try:
        cdata = loadDaily(atmp)
        ax.boxplot(
            cdata.data.compressed(),
            positions=[offset - 1 / 5],
            widths=1 / 3,
            whis=(0, 100),
            showcaps=False,
            medianprops={"color": "black"},
            whiskerprops={"color": bColour},
            boxprops={"facecolor": bColour},
            patch_artist=True,
        )
    except Exception:
        pass
    # ukpp box
    atmp.source = "UKPP"
    atmp.type = args.type
    bColour = (255 / 255, 152 / 255, 150 / 255)  # T10 red light
    if offset == 0:
        bColour = (214 / 255, 39 / 255, 40 / 255)  # T10 red
    try:
        cdata = loadDaily(atmp)
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
    except Exception:
        pass


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
    "size": 14,
}
matplotlib.rc("font", **font)
axb = fig.add_axes([0, 0, 1, 1])
ax_ts = fig.add_axes([0.03, 0.07, 0.96, 0.9])
ax_ts.set_ylim(args.vMin, args.vMax)
ax_ts.set_xlim(args.dayrange * -1 - 0.5, args.dayrange + 0.5)
ax_ts.set_aspect("auto")

ticL = []
ticV = []
dte = datetime.date(args.year, args.month, args.day)
for offset in range(args.dayrange * -1, args.dayrange + 1):
    box_1_day(args, offset, ax_ts)
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

ax_ts.set_xticks(ticV)
ax_ts.set_xticklabels(ticL)

fig.savefig("%s/TS_%s.png" % (opdir, args.type))

#!/usr/bin/env python

# Plot haduk-grid/Improver Tmax

import os
import sys
import numpy as np

import iris
import iris.analysis
import warnings
warnings.filterwarnings("ignore", category=iris.fileformats.netcdf.UnknownCellMethodWarning)

sys.path.append("%s/../../../utils/plots" % os.path.dirname(__file__))
from HUKG_load_tmax import HUKG_load_tmax
from HUKG_load_tmax import HUKG_load_tmax_climatology

sys.path.append("%s/." % os.path.dirname(__file__))
from Improver_load_tmax import Improver_load_tmax

sys.path.append("%s/../../../utils/plots/maps" % os.path.dirname(__file__))
from plotTmax import plotTmax

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
    "--source",
    help="haduk-grid, or Improver",
    choices=["haduk-grid", "Improver"],
    type=str,
    required=True,
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

# Get a land-sea mask
mask = iris.load_cube(
    "%s/fixed_fields/land_mask/HadUKG_land_from_Copernicus.nc" % os.getenv("DATADIR"),
    iris.Constraint(
        projection_y_coordinate=lambda cell: args.latMin * 1000
        <= cell
        <= args.latMax * 1000
    )
    & iris.Constraint(
        projection_x_coordinate=lambda cell: args.lonMin * 1000
        <= cell
        <= args.lonMax * 1000
    ),
)

# Load the source data
if args.source == "haduk-grid":
    sdata = HUKG_load_tmax(args)
elif args.source == "Improver":
    sdata = Improver_load_tmax(args)

# Load the other source - we may need it to make the ranges match
if args.source == "Improver":
    ddata = HUKG_load_tmax(args)
elif args.source == "haduk-grid":
    ddata = Improver_load_tmax(args)

# Subtract the climatology, if anomalies wanted
#  (or if differences wanted, as we'll need the anomaly range for comparison)
if args.type == "anomalies" or args.type == "differences":
    cdata = HUKG_load_tmax_climatology(args)
    cdata = cdata.regrid(sdata, iris.analysis.Nearest())
    sdata = sdata - cdata
    cdata = cdata.regrid(ddata, iris.analysis.Nearest())
    ddata = ddata - cdata

# Set defaults for the range, if not specified
if args.vMax is None:
    if args.type == "actuals":
        args.vMax = max(np.max(sdata.data), np.max(ddata.data))
    if args.type == "anomalies":
        args.vMax = max(
            np.max(sdata.data),
            np.max(ddata.data),
            np.min(sdata.data) * -1,
            np.min(ddata.data) * -1,
        )
    if args.type == "differences":
        args.vMax = max(
            np.max(sdata.data),
            np.max(ddata.data),
            np.min(sdata.data) * -1,
            np.min(ddata.data) * -1,
        )
if args.vMin is None:
    if args.type == "anomalies" or args.type == "differences":
        args.vMin = args.vMax * -1
    else:
        args.vMin = min(np.min(sdata.data), np.min(ddata.data))

# Subtract the other source, if differences wanted
if args.type == "differences":
    sdata = sdata - ddata

# Make the plot
plotTmax(
    sdata,
    vMax=args.vMax,
    vMin=args.vMin,
    latMax=args.latMax,
    latMin=args.latMin,
    lonMax=args.lonMax,
    lonMin=args.lonMin,
    height=11 * 1.61,
    width=11,
    opDir=opdir,
    fName="%s_map_%03d_%s.png" % (args.source, args.lead_time, args.type),
    lMask=mask,
)

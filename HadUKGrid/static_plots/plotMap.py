#!/usr/bin/env python

# Plot HadUKGrid Tmax

import os
import sys
import numpy as np

import iris
import iris.analysis

sys.path.append("%s/./HUKG" % os.path.dirname(__file__))
from HUKG_load_tmax import HUKG_load_tmax
from HUKG_load_tmax import HUKG_load_tmax_climatology

sys.path.append("%s/./UKPP" % os.path.dirname(__file__))
from UKPP_load_tmax import UKPP_load_tmax

sys.path.append("%s/./maps" % os.path.dirname(__file__))
from plotTmax import plotTmax

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--year", help="Year", type=int, required=True)
parser.add_argument("--month", help="Integer month", type=int, required=True)
parser.add_argument("--day", help="Day of month", type=int, required=True)
parser.add_argument(
    "--source",
    help="HadUKGrid, or UKPP",
    choices=["HadUKGrid", "UKPP"],
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
    fName="%s_map_%s.png" % (args.source, args.type),
    lMask=mask,
)

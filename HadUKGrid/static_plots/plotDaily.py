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
if not os.path.isdir(args.opdir):
    os.makedirs(args.opdir)

opdir = None
if args.opdir is None:
    opdir = "%s/figures/HadUKGrid/daily/Tmax/%04d/%02d/%02d" % (
        os.getenv("SCRATCH"),
        args.year,
        args.month,
        args.day,
    )
else:
    opdir = args.opdir

# Get a land-sea mask
mask = iris.load_cube(
    "%s/fixed_fields/land_mask/HadUKG_land_from_Copernicus.nc" % os.getenv("DATADIR"),
)

# Load the source data
if args.source == "HadUKGrid":
    sdata = HUKG_load_tmax(args.year, args.month, args.day)
elif args.source == "UKPP":
    sys.exit(1)

# Subtract the climatology, if anomalies wanted
if args.type == "anomalies":
    cdata = HUKG_load_tmax_climatology(args.year, args.month, args.day)
    cdata = cdata.regrid(sdata, iris.analysis.Nearest())
    sdata = sdata - cdata

# Subtract the other source, if differences wanted
if args.type == "differences":
    if args.source == "UKPP":
        ddata = HUKG_load_tmax(args.year, args.month, args.day)
    elif args.source == "HadUKGrid":
        sys.exit(1)
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
    fName="%s.png" % args.type,
    lMask=mask,
)

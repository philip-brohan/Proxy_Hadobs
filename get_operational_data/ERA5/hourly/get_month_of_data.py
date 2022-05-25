#!/usr/bin/env python

# Retrieve surface weather variable from ERA5.
#  Every hour in one calendar month
import os
import cdsapi
from calendar import monthrange

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--variable", help="Variable name", type=str, required=True)
parser.add_argument("--year", help="Year", type=int, required=True)
parser.add_argument("--month", help="Integer month", type=int, required=True)
parser.add_argument(
    "--opdir",
    help="Directory for output files",
    default="%s/opfc/ERA5/hourly" % os.getenv("SCRATCH"),
)
args = parser.parse_args()
opdir = "%s/%04d/%02d" % (args.opdir, args.year, args.month)
if not os.path.isdir(opdir):
    os.makedirs(opdir)
c = cdsapi.Client()

c.retrieve(
    "reanalysis-era5-single-levels",
    {
        "product_type": "reanalysis",
        "format": "netcdf",
        "variable": args.variable,
        "year": "%04d" % args.year,
        "month": "%02d" % args.month,
        "day": [
            "%02d" % day for day in range(1, monthrange(args.year, args.month)[1] + 1)
        ],
        "time": [
            "00:00",
            "01:00",
            "02:00",
            "03:00",
            "04:00",
            "05:00",
            "06:00",
            "07:00",
            "08:00",
            "09:00",
            "10:00",
            "11:00",
            "12:00",
            "13:00",
            "14:00",
            "15:00",
            "16:00",
            "17:00",
            "18:00",
            "19:00",
            "20:00",
            "21:00",
            "22:00",
            "23:00",
        ],
    },
    "%s/%s.nc" % (opdir, args.variable),
)

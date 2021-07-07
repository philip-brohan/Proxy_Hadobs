#!/usr/bin/env python

# Make daily (9am-9am) Tmax from the UKPP data, on the haduk-grid Grid

import os
import sys
import iris
import datetime
import numpy as np

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--year", type=int, required=True)
parser.add_argument("--month", type=int, required=True)
parser.add_argument("--day", type=int, required=True)
parser.add_argument(
    "--lead_time",
    type=int,
    required=False,
    default=0,
    help="Forecast lead time in hours",
)
parser.add_argument(
    "--adjustment",
    type=str,
    required=False,
    default="raw",
    help="Algorithem used to adjust forecast data to match obs.",
)
args = parser.parse_args()

# Load the adjustment function
sys.path.append("%s/./adjustments/%s" % (os.path.dirname(__file__), args.adjustment))
from adjust import adjust

# Use a climatology file for the grid definition
def get_HUKG_cube_for_grid():
    HUKG_grid = iris.load_cube(
        "/data/users/haduk/uk_climate_data/supported/"
        + "haduk-grid/v1.0.3.0/data/grid_archives/"
        + "lta_archive_v1/grid/monthly_maxtemp_climatology/"
        + "1981-2010/jan.nc"
    )
    return HUKG_grid


# Directory for storing the forecast data
Mdir = "%s/Proxy_Hadobs/opfc/UKPP/" % (os.getenv("SCRATCH"))

# Directory for storing the proxy data
Pdir = "%s/Proxy_Hadobs/proxy_datasets/haduk-grid/daily_maxtemp/UKPP/%s/%03d" % (
    os.getenv("SCRATCH"),
    args.adjustment,
    args.lead_time,
)


def get_PP_file_for_dtime(dte):
    fname = ("%s/%04d%02d%02d/" + "%04d%02d%02d%02d00_u1096_ng_pp_temperature_2km") % (
        Mdir,
        dte.year,
        dte.month,
        dte.day,
        dte.year,
        dte.month,
        dte.day,
        dte.hour,
    )
    return fname


# Get data with given validity time. Use forecast at leadTime if possible
#  if that data is missing, try increasing the leadTime.
def get_data_for_hour(year, month, day, hour, lead_time):
    offset = 0
    fname = None
    while fname is None:
        dte = (
            datetime.datetime(year, month, day, hour)
            - datetime.timedelta(hours=lead_time)
            - datetime.timedelta(seconds=offset)
        )
        fn = get_PP_file_for_dtime(dte)
        if os.path.isfile(fn):
            fname = fn
            break
        offset += 3600
        if offset > 21600 - lead_time * 3600:
            raise OSError(
                "No data on disc for %04d-%02d-%02d:%02d" % (year, month, day, hour)
            )
    hdata = iris.load_cube(
        fname,
        iris.Constraint(forecast_period=lead_time * 3600 + offset)
        & iris.Constraint(name="temperature")
        & iris.AttributeConstraint(source="Post Processing"),
    )
    return hdata


# Get the 9am-9am maximum in the PP data
dtstart = datetime.datetime(args.year, args.month, args.day, 9)
tmax = get_data_for_hour(
    dtstart.year, dtstart.month, dtstart.day, dtstart.hour, args.lead_time
)
for offset in range(1, 25):  # Include both 9ams in period
    dto = dtstart + datetime.timedelta(hours=offset)
    tt = get_data_for_hour(dto.year, dto.month, dto.day, dto.hour, args.lead_time)
    tmax.data = np.maximum(tmax.data, tt.data)

# Regrid to match HadUKGrid
HGG = get_HUKG_cube_for_grid()
tmax = tmax.regrid(HGG, iris.analysis.Linear())
# Apply the HadUKGrid data mask
# Why doesn't this happen automatically?
tmax.data = np.ma.masked_array(tmax.data, HGG.data.mask)

# Store the proxy tmax
sfile = "%s/%04d/%02d/%02d.nc" % (Pdir, args.year, args.month, args.day)
if not os.path.isdir(os.path.dirname(sfile)):
    os.makedirs(os.path.dirname(sfile))
iris.save(tmax, sfile)

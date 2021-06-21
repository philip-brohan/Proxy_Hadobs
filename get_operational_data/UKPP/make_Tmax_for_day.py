#!/usr/bin/env python

# Make daily (9am-9am) Tmax from the UKPP data, on the HadUKGrid Grid

import os
import iris
import datetime
import numpy as np

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--year", type=int, required=True)
parser.add_argument("--month", type=int, required=True)
parser.add_argument("--day", type=int, required=True)
args = parser.parse_args()

# Use a climatology file for the grid definition
def get_HUKG_cube_for_grid():
    HUKG_grid = iris.load_cube(
        "/data/users/haduk/uk_climate_data/supported/"
        + "haduk-grid/v1.0.3.0/data/grid_archives/"
        + "lta_archive_v1/grid/monthly_maxtemp_climatology/"
        + "1981-2010/jan.nc"
    )
    return HUKG_grid


# Directory for storing the proxy data
Pdir = "%s/Proxy_Hadobs/opfc/UKPP/" % os.getenv("SCRATCH")


def get_PP_file_for_dtime(dte):
    fname = ("%s/%04d%02d%02d/" + "%04d%02d%02d%02d00_u1096_ng_pp_temperature_2km") % (
        Pdir,
        dte.year,
        dte.month,
        dte.day,
        dte.year,
        dte.month,
        dte.day,
        dte.hour,
    )
    return fname


# Get analysis if possible, if analysis is missing, use forecast.
def get_data_for_hour(year, month, day, hour):
    offset = 0
    fname = None
    while fname is None:
        dte = datetime.datetime(year, month, day, hour) - datetime.timedelta(
            hours=offset
        )
        fn = get_PP_file_for_dtime(dte)
        if os.path.isfile(fn):
            fname = fn
            break
        offset += 1
        if offset > 6:
            raise OSError(
                "No data on disc for %04d-%02d-%02d:%02d" % (year, month, day, hour)
            )
    hdata = iris.load_cube(
        fname,
        iris.Constraint(forecast_period=offset)
        & iris.Constraint(name="temperature")
        & iris.AttributeConstraint(source="Post Processing"),
    )
    return hdata


# Get the 9am-9am maximum in the PP data
dtstart = datetime.datetime(args.year, args.month, args.day, 9)
tmax = get_data_for_hour(dtstart.year, dtstart.month, dtstart.day, dtstart.hour)
for offset in range(1, 25):  # Include both 9ams in period
    dto = dtstart + datetime.timedelta(hours=offset)
    tt = get_data_for_hour(dto.year, dto.month, dto.day, dto.hour)
    tmax.data = np.maximum(tmax.data, tt.data)

# Regrid to match HadUKGrid
HGG = get_HUKG_cube_for_grid()
tmax = tmax.regrid(HGG, iris.analysis.Linear())
# Apply the HadUKGrid data mask
# Why doesn't this happen automatically?
tmax.data = np.ma.masked_array(tmax.data, HGG.data.mask)

# Store the proxy tmax
sfile = "%s/%04d%02d%02d/HUKG_Proxy_tasmax.nc" % (Pdir, args.year, args.month, args.day)
iris.save(tmax, sfile)

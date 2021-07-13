#!/usr/bin/env python

# Make daily (9am-9am) Tmax from the Improver data, on the haduk-grid Grid

import os
import sys
import iris
import glob
import datetime
import numpy as np
from iris.analysis import Aggregator

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
Mdir = "%s/Proxy_Hadobs/opfc/Improver/" % (os.getenv("SCRATCH"))

# Directory for storing the proxy data
Pdir = "%s/Proxy_Hadobs/proxy_datasets/haduk-grid/daily_maxtemp/Improver/%s/%03d" % (
    os.getenv("SCRATCH"),
    args.adjustment,
    args.lead_time,
)


# Get data with given validity time, and the smallest available leadtime >=
#  that specified.
def get_data_for_hour(year, month, day, hour, lead_time):
    dirname = "%s/temperature_at_screen_level/%04d/%02d/%02d/%02d" % (
        Mdir,
        year,
        month,
        day,
        hour,
    )
    ffiles = glob.glob("%s/*.nc" % dirname)
    cFile = None
    cLead = None
    vTime = datetime.datetime(year, month, day, hour)
    for file in ffiles:
        bIDX = file.find("B")
        bTime = datetime.datetime(
            int(file[(bIDX + 1) : (bIDX + 5)]),
            int(file[(bIDX + 5) : (bIDX + 7)]),
            int(file[(bIDX + 7) : (bIDX + 9)]),
            int(file[(bIDX + 10) : (bIDX + 12)]),
            int(file[(bIDX + 12) : (bIDX + 14)]),
        )
        fLead = (vTime - bTime).total_seconds() / 3600
        if fLead >= lead_time:
            if cLead is None or cLead > fLead:
                cFile = file
                cLead = fLead
    if cFile is None:
        raise Exception(
            "No data on disc for %s at %d lead"
            % (vTime.strftime("%Y-%M-%D:%H"), lead_time)
        )
    hdata = iris.load_cube(
        cFile,
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

# Sample randomly from the percentiles to reduce to 2d
def sample1d(data, axis=0):
    rng = np.random.default_rng()
    return rng.choice(data, axis=axis)


SAMPLE = Aggregator("Random sample", sample1d)
tmax = tmax.collapsed("percentile", SAMPLE)

# Regrid to match HadUKGrid
HGG = get_HUKG_cube_for_grid()
tmax = tmax.regrid(HGG, iris.analysis.Linear())
# Apply the HadUKGrid data mask
# Why doesn't this happen automatically?
tmax.data = np.ma.masked_array(tmax.data, HGG.data.mask)

# Store the proxy tmax
sfile = "%s/%04d/%02d/%02d.nc" % (
    Pdir,
    args.year,
    args.month,
    args.day,
)
if not os.path.isdir(os.path.dirname(sfile)):
    os.makedirs(os.path.dirname(sfile))
iris.save(tmax, sfile)

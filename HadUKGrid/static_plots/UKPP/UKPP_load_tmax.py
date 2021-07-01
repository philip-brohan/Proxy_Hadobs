# Load temperature data from the UKPP analysis

import os
import iris
import numpy as np


def UKPP_load_tmax(args):
    dirname = "%04d%02d%02d" % (args.year, args.month, args.day)
    filename = "HUKG_Proxy_tasmax.nc"
    hdata = iris.load_cube(
        "%s/Proxy_Hadobs/opfc/UKPP/%s/%s" % (os.getenv("SCRATCH"), dirname, filename),
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
    return hdata


def UKPP_load_hourly(year, month, day, hour):
    dirname = "%04d%02d%02d" % (year, month, day)
    filename = "%04d%02d%02d%02d00_u1096_ng_pp_temperature_2km" % (
        year,
        month,
        day,
        hour,
    )
    # Want the PP data
    hdata = iris.load_cube(
        "%s/Proxy_Hadobs/opfc/UKPP/%s/%s" % (os.getenv("SCRATCH"), dirname, filename),
        iris.Constraint(forecast_period=0)
        & iris.Constraint(name="temperature")
        & iris.AttributeConstraint(source="Post Processing"),
    )
    return hdata

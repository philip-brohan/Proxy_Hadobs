# Load temperature data from the UKPP analysis

import os
import iris
import numpy as np


def UKPP_load_tmax(year, month, day):
    dirname = "%04d%02d%02d" % (year, month, day)
    filename = "HUKG_Proxy_tasmax.nc"
    hdata = iris.load_cube(
        "%s/Proxy_Hadobs/opfc/UKPP/%s/%s" % (os.getenv("SCRATCH"), dirname, filename)
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
    # But only the land data, so get the mask from the MOSES data
    mdata = iris.load_cube(
        "%s/Proxy_Hadobs/opfc/UKPP/%s/%s" % (os.getenv("SCRATCH"), dirname, filename),
        iris.Constraint(forecast_period=0)
        & iris.Constraint(name="temperature")
        & iris.AttributeConstraint(source="MOSES-PDM-RFM"),
    )
    # Mask out the sea data
    # hdata.data[mdata.data.mask==True]=np.nan
    return hdata

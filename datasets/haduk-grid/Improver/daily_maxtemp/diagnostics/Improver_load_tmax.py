# Load daily_maxtemp data from Improver

import os
import iris


def Improver_load_tmax(args):
    filename = (
        "%s/Proxy_Hadobs/proxy_datasets/haduk-grid/daily_maxtemp/Improver/"
        + "%s/%03d/%04d/%02d/%02d.nc"
    ) % (
        os.getenv("SCRATCH"),
        args.adjustment,
        args.lead_time,
        args.year,
        args.month,
        args.day,
    )
    hdata = iris.load_cube(
        filename,
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
    # Set same units as haduk-grid
    hdata.convert_units("celsius")
    return hdata

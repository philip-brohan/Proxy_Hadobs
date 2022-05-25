#!/usr/bin/env python

# Get hourly ERA5 data for several months, and store on SCRATCH.

import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--startyear", type=int, required=True)
parser.add_argument("--startmonth", type=int, required=True)
parser.add_argument("--endyear", type=int, required=True)
parser.add_argument("--endmonth", type=int, required=True)
args = parser.parse_args()

for year in range(args.startyear, args.endyear + 1):
    for month in range(1, 13):
        if (year == args.startyear and month < args.startmonth) or (
            year == args.endyear and month > args.endmonth
        ):
            continue
        for var in [
            "2m_temperature",
            "mean_sea_level_pressure",
            "10m_u_component_of_wind",
            "10m_v_component_of_wind",
            "sea_surface_temperature",
            "total_precipitation",
        ]:
            opfile = "%s/opfc/ERA5/hourly/%04d/%02d/%s.nc" % (
                os.getenv("SCRATCH"),
                year,
                month,
                var,
            )
            if not os.path.isfile(opfile):
                print(
                    ("./get_month_of_data.py --year=%d --month=%d --variable=%s")
                    % (year, month, var,)
                )

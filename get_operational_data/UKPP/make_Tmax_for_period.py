#!/usr/bin/env python

# Make daily Tmax from UKPP for many days

import os
import datetime
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--startyear", type=int, required=True)
parser.add_argument("--startmonth", type=int, required=True)
parser.add_argument("--startday", type=int, required=True)
parser.add_argument("--endyear", type=int, required=True)
parser.add_argument("--endmonth", type=int, required=True)
parser.add_argument("--endday", type=int, required=True)
args = parser.parse_args()

current = datetime.date(args.startyear, args.startmonth, args.startday)
endd = datetime.date(args.endyear, args.endmonth, args.endday)

while current <= endd:
    ofile = "%s/Proxy_Hadobs/opfc/UKPP/%04d%02d%02d/HUKG_Proxy_tasmax.nc" % (
        os.getenv("SCRATCH"),
        current.year,
        current.month,
        current.day,
    )
    if not os.path.isfile(ofile):
        print(
            "./make_Tmax_for_day.py --year=%d --month=%d --day=%d"
            % (current.year, current.month, current.day)
        )
    current += datetime.timedelta(days=1)

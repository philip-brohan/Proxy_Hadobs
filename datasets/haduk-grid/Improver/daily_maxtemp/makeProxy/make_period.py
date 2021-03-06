#!/usr/bin/env python

# Make all the Tmax proxy datasets for a range of dates
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

dts = datetime.date(args.startyear, args.startmonth, args.startday)
dte = datetime.date(args.endyear, args.endmonth, args.endday)

while dts <= dte:
    for adjustment in ["raw"]:
        for lead in (0, 24, 48, 72, 96, 120, 144, 168):
            print(
                (
                    "./make_Tmax_for_day.py --year=%d --month=%d --day=%d "
                    + "--adjustment=%s --lead_time=%d"
                )
                % (dts.year, dts.month, dts.day, adjustment, lead)
            )
    dts += datetime.timedelta(days=1)

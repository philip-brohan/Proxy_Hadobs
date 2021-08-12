#!/usr/bin/env python

# Make all the Tmax proxy datasets using data from one day
# so the 0 hour forcast for that day, the 24 hour forecast for the next day,
#  ... the 168 hour forecast for 7 days ahead.

import datetime

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--year", type=int, required=True)
parser.add_argument("--month", type=int, required=True)
parser.add_argument("--day", type=int, required=True)
args = parser.parse_args()

dts = datetime.date(args.year, args.month, args.day)

for lead in (0, 24, 48, 72, 96, 120, 144, 168):
    dtc = dts + datetime.timedelta(days=lead//24)
    for adjustment in ["raw"]:
        print(
            (
                "./make_Tmax_for_day.py --year=%d --month=%d --day=%d "
                + "--adjustment=%s --lead_time=%d"
            )
            % (dtc.year, dtc.month, dtc.day, adjustment, lead)
        )

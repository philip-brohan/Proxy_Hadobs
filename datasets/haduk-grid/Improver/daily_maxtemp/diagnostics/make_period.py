#!/usr/bin/env python

# Make all the Tmax proxy diagnostics for a range of dates
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
            for type in ("actuals", "anomalies", "differences"):
                print(
                    (
                        "./plotTS.py --year=%d --month=%d --day=%d "
                        + "--adjustment=%s --lead_time=%d --type=%s"
                    )
                    % (dts.year, dts.month, dts.day, adjustment, lead, type)
                )
                print(
                    (
                        "./plotMap.py --year=%d --month=%d --day=%d "
                        + "--adjustment=%s --lead_time=%d --type=%s --source=Improver"
                    )
                    % (dts.year, dts.month, dts.day, adjustment, lead, type)
                )
                if type == "differences":
                    continue
                print(
                    (
                        "./plotMap.py --year=%d --month=%d --day=%d "
                        + "--adjustment=%s --lead_time=%d --type=%s --source=HadUKGrid"
                    )
                    % (dts.year, dts.month, dts.day, adjustment, lead, type)
                )

    dts += datetime.timedelta(days=1)

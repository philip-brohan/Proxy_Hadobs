#!/usr/bin/env python

# Make Tmax comparison plots and UI for many days

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
    print(
        "./allPlotsOneDay.py --year=%d --month=%d --day=%d"
        % (current.year, current.month, current.day)
    )
    for pType in ('actuals','anomalies','differences'):
        print(
            "./webUI/makeUI.py --year=%d --month=%d --day=%d --type=%s"
            % (current.year, current.month, current.day,pType)
        )
    current += datetime.timedelta(days=1)

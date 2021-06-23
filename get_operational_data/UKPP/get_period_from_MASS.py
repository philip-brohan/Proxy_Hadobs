#!/usr/bin/env python

# Get UKPP fields for many days from MASS, and store on SCRATCH.

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
        "./get_day_from_MASS.py --year=%d --month=%d --day=%d"
        % (current.year, current.month, current.day)
    )
    current += datetime.timedelta(days=1)

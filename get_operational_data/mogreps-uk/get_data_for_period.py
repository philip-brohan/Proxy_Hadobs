#!/usr/bin/env python

# Get mogreps-uk fields for many days from MASS, and store on SCRATCH.

import os
import datetime
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--startyear", type=int, required=True)
parser.add_argument("--startmonth", type=int, required=True)
parser.add_argument("--startday", type=int, required=True)
parser.add_argument("--starthour", type=int, required=False, default=0)
parser.add_argument("--endyear", type=int, required=True)
parser.add_argument("--endmonth", type=int, required=True)
parser.add_argument("--endday", type=int, required=True)
parser.add_argument("--endhour", type=int, required=False, default=23)
parser.add_argument("--lead", type=int, required=False, default=3)
args = parser.parse_args()

current = datetime.datetime(
    args.startyear, args.startmonth, args.startday, args.starthour
)
endd = datetime.datetime(args.endyear, args.endmonth, args.endday, args.endhour, 59, 59)

while current <= endd:
    opfile = "%s/opfc/mogreps-uk/%04d/%02d/%02d_%02d_%03d.pp" % (
        os.getenv("SCRATCH"),
        current.year,
        current.month,
        current.day,
        current.hour,
        args.lead,
    )
    if not os.path.isfile(opfile):
        print(
            "./get_data_for_hour.py --year=%d --month=%d --day=%d --hour=%d --lead=%d"
            % (current.year, current.month, current.day, current.hour, args.lead)
        )
    current += datetime.timedelta(hours=1)

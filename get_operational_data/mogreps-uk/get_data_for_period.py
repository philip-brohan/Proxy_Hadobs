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
parser.add_argument("--max_lead", type=int, required=False, default=6)
parser.add_argument("--min_lead", type=int, required=False, default=0)
args = parser.parse_args()

current = datetime.datetime(
    args.startyear, args.startmonth, args.startday, args.starthour
)
endd = datetime.datetime(args.endyear, args.endmonth, args.endday, args.endhour, 59, 59)

while current <= endd:
    opfile_c = "%s/opfc/mogreps-uk/%04d/%02d/%02d/%02d_%03d_%03d_c.pp" % (
        os.getenv("SCRATCH"),
        current.year,
        current.month,
        current.day,
        current.hour,
        args.min_lead,
        args.max_lead,
    )
    opfile_p = "%s/opfc/mogreps-uk/%04d/%02d/%02d/%02d_%03d_%03d_p.pp" % (
        os.getenv("SCRATCH"),
        current.year,
        current.month,
        current.day,
        current.hour,
        args.min_lead,
        args.max_lead,
    )
    if not os.path.isfile(opfile_c) and not os.path.isfile(opfile_p):
        print(
            (
                "./get_data_for_hour.py --year=%d --month=%d --day=%d --hour=%d "
                + "--min_lead=%d --max_lead=%d"
            )
            % (
                current.year,
                current.month,
                current.day,
                current.hour,
                args.min_lead,
                args.max_lead,
            )
        )
    current += datetime.timedelta(hours=1)

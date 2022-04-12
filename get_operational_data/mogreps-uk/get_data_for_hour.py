#!/usr/bin/env python

# Retrieve surface weather variables from the mogreps-uk analysis
#  for one hour.
# Gets data from all available forecasts for one given validity time.

import os
import sys
from tempfile import NamedTemporaryFile
import subprocess
import datetime

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--year", help="Year", type=int, required=True)
parser.add_argument("--month", help="Integer month", type=int, required=True)
parser.add_argument("--day", help="Day of month", type=int, required=True)
parser.add_argument("--hour", help="Hour of day", type=int, required=True)
parser.add_argument(
    "--max_lead", help="max lead time (hours)", type=int, required=False, default=130
)
parser.add_argument(
    "--min_lead", help="min lead time (hours)", type=int, required=False, default=0
)
parser.add_argument(
    "--opdir",
    help="Directory for output files",
    default="%s/opfc/mogreps-uk" % os.getenv("SCRATCH"),
)
args = parser.parse_args()
opdir = "%s/%04d/%02d/%02d" % (args.opdir, args.year, args.month, args.day)
if not os.path.isdir(opdir):
    os.makedirs(opdir)

print("%04d-%02d-%02d:%02d" % (args.year, args.month, args.day, args.hour))

target_d = datetime.datetime(args.year, args.month, args.day, args.hour)

# Does a mass file contain data for the selected date
def keep_file(fname):
    lead = int(fname[-6:-3])
    hour = int(fname[-12:-10])
    day = int(fname[-15:-13])
    month = int(fname[-17:-15])
    year = int(fname[-21:-17])
    rund = datetime.datetime(year, month, day, hour)
    leadh = int((target_d - rund).total_seconds() / 3600)
    if (
        leadh < args.max_lead
        and leadh > args.min_lead
        and leadh < lead
        and leadh >= (lead - 3)
    ):
        return True
    return False


# Get all available files for given  month
def files_for_month(year, month):
    mr = subprocess.run(
        ["moo", "ls", "moose:/opfc/atm/mogreps-uk/prods/%04d%02d.pp" % (year, month),],
        capture_output=True,
        text=True,
    )
    mr.check_returncode()  # Throw exception if moose call failed
    mf = mr.stdout.split("\n")
    flist = []
    for fn in mf:
        if len(fn) > 21 and keep_file(fn):
            flist.append(fn)
    return flist


# Run a retrieval
def run_retrieval(flist, mass_dir, opfile):
    qfile = NamedTemporaryFile(mode="w+", delete=False)
    qfile.write("begin_global\n")
    qfile.write("   pp_file = (")
    for ppfl in flist:
        qfile.write('"%s"' % os.path.basename(ppfl))
        if ppfl != flist[-1]:
            qfile.write(",")
        else:
            qfile.write(")\n")
    qfile.write("end_global\n")
    qfile.write("begin\n")
    qfile.write("    stash = (16222,3236,3225,3226,4203,4204)\n")
    qfile.write("    lbproc = 0\n")
    qfile.write("    yr = %d\n" % args.year)
    qfile.write("    mon = %d\n" % args.month)
    qfile.write("    day = %d\n" % args.day)
    qfile.write("    hr = %d\n" % args.hour)
    qfile.write("end\n")
    qfile.close()

    # Run the query
    # opfile = "%s/%02d_%02d_%03d.pp" % (opdir, args.day, args.hour, args.lead)
    subprocess.call(
        "moo select -C %s %s %s" % (qfile.name, mass_dir, opfile), shell=True
    )

    os.remove(qfile.name)


# Get all data archived in the current month's directory
flist = files_for_month(args.year, args.month)
if len(flist) > 0:
    run_retrieval(
        flist,
        "moose:/opfc/atm/mogreps-uk/prods/%04d%02d.pp" % (args.year, args.month),
        "%s/%02d_%03d_%03d_c.pp" % (opdir, args.hour, args.min_lead, args.max_lead),
    )
mlead = (args.day - 1) * 24 + args.hour
if args.max_lead > mlead:
    year = args.year
    month = args.month - 1
    if month < 1:
        year -= 1
        month = 12
    flist = files_for_month(year, month)
    if len(flist) > 0:
        run_retrieval(
            flist,
            "moose:/opfc/atm/mogreps-uk/prods/%04d%02d.pp" % (year, month),
            "%s/%02d_%03d_%03d_p.pp" % (opdir, args.hour, args.min_lead, args.max_lead),
        )

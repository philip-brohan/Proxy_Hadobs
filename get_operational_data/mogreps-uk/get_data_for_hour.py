#!/usr/bin/env python

# Retrieve surface weather variables from the mogreps-uk analysis
#  for one day.

import os
import sys
from tempfile import NamedTemporaryFile
import subprocess

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--year", help="Year", type=int, required=True)
parser.add_argument("--month", help="Integer month", type=int, required=True)
parser.add_argument("--day", help="Day of month", type=int, required=True)
parser.add_argument("--hour", help="Hour of day", type=int, required=True)
parser.add_argument(
    "--lead", help="lead time (hours)", type=int, required=False, default=3
)
parser.add_argument(
    "--opdir",
    help="Directory for output files",
    default="%s/opfc/mogreps-uk" % os.getenv("SCRATCH"),
)
args = parser.parse_args()
opdir = "%s/%04d/%02d" % (args.opdir, args.year, args.month)
if not os.path.isdir(opdir):
    os.makedirs(opdir)

print("%04d-%02d-%02d:%02d" % (args.year, args.month, args.day, args.hour))

# Mass directory to use
mass_dir = "moose:/opfc/atm/mogreps-uk/prods/%04d%02d.pp" % (args.year, args.month)

# Files to retrieve from
flist = []
for member in range(34):
    hour = args.hour
    fcst = args.lead
    flist.append(
        "prods_op_mogreps-uk_%04d%02d%02d_%02d_%02d_%03d.pp"
        % (args.year, args.month, args.day, hour, member, fcst)
    )

# Create the query file
qfile = NamedTemporaryFile(mode="w+", delete=False)
qfile.write("begin_global\n")
qfile.write("   pp_file = (")
for ppfl in flist:
    qfile.write('"%s"' % ppfl)
    if ppfl != flist[-1]:
        qfile.write(",")
    else:
        qfile.write(")\n")
qfile.write("end_global\n")
qfile.write("begin\n")
qfile.write("    stash = (16222,3236,3225,3226,4203,4204)\n")
qfile.write("    lbproc = 0\n")
qfile.write("end\n")
qfile.close()

# Run the query
opfile = "%s/%02d_%02d_%03d.pp" % (opdir, args.day, args.hour, args.lead)
subprocess.call("moo select -C %s %s %s" % (qfile.name, mass_dir, opfile), shell=True)

os.remove(qfile.name)

#!/usr/bin/env python

# Retrieve downloaded mogreps-uk data from MASS

import sys
import os
import os.path
import glob
import tarfile
import afterburner.io.moose2 as moose

# What to retrieve
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--year", help="Year", type=int, required=True)
parser.add_argument("--month", help="Integer month", type=int, required=True)
parser.add_argument(
    "--min_lead", help="min lead time (hours)", type=int, required=False, default=0
)
parser.add_argument(
    "--max_lead", help="max lead time (hours)", type=int, required=False, default=6
)
args = parser.parse_args()

# Check moose availability
if not moose.has_moose_support():
    raise Exception("Moose unavailable")
if not moose.check_moose_commands_enabled(moose.MOOSE_LS):
    raise Exception("'moo ls' disabled")
if not moose.check_moose_commands_enabled(moose.MOOSE_GET):
    raise Exception("'moo get' disabled")

# Base location for storage
mbase = "moose:/adhoc/users/philip.brohan"
moose_dir = "%s/opfc/mogreps-uk/%04d" % (mbase, args.year)

# Disc data dir
ddir = "%s/opfc/mogreps-uk/%04d" % (os.environ["SCRATCH"], args.year)
if not os.path.isdir(ddir):
    os.makedirs(ddir)

# Data to retrieve?
if (
    moose.run_moose_command(
        "moo test -f %s/%02d_%03d_%03d.tar"
        % (moose_dir, args.month, args.min_lead, args.max_lead)
    )[0]
    == "false"
):
    raise Exception(
        "%04d-%02d lead %03d to %03d not on archive"
        % (args.year, args.month, args.min_lead, args.max_lead)
    )


# Retrtieve the archive tar file
otarf = "%02d_%03d_%03d.tar" % (args.month, args.min_lead, args.max_lead,)
moose.get(ddir, "%s/%s" % (moose_dir, otarf))

# Unpack to pp files
tf = tarfile.open(name="%s/%s" % (ddir, otarf), mode="r")
tf.extractall(ddir)
tf.close()

# Reset the modification time -
#     otherwise scratch will delete them.
members = glob.glob(
    "%s/%02d/*/*_%03d_%03d_*.pp" % (ddir, args.month, args.min_lead, args.max_lead)
)
for member in members:
    os.utime(member, None)

# Clean up
os.remove("%s/%s" % (ddir, otarf))

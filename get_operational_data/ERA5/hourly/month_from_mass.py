#!/usr/bin/env python

# Retrieve downloaded ERA5 hourly data from MASS

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
moose_dir = "%s/opfc/ERA5/hourly/%04d" % (mbase, args.year)

# Disc data dir
ddir = "%s/opfc/ERA5/hourly/%04d" % (os.environ["SCRATCH"], args.year)
if not os.path.isdir(ddir):
    os.makedirs(ddir)

# Data to retrieve?
if (
    moose.run_moose_command("moo test -f %s/%02d.tar" % (moose_dir, args.month))[0]
    == "false"
):
    raise Exception("%04d-%02d not on archive" % (args.year, args.month))


# Retrtieve the archive tar file
otarf = "%02d.tar" % args.month
moose.get(ddir, "%s/%s" % (moose_dir, otarf))

# Unpack to pp files
tf = tarfile.open(name="%s/%s" % (ddir, otarf), mode="r")
tf.extractall(ddir)
tf.close()

# Reset the modification time -
#     otherwise scratch will delete them.
members = glob.glob("%s/%02d/*.nc" % (ddir, args.month))
for member in members:
    os.utime(member, None)

# Clean up
os.remove("%s/%s" % (ddir, otarf))

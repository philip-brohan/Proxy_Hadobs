#!/usr/bin/env python

# Archive downloaded ERA5 hourly data to MASS
# Batched up as 1 months data for all variables

import sys
import os
import subprocess
import os.path
import glob
import tarfile
import afterburner.io.moose2 as moose

# What to store
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--year", help="Year", type=int, required=True)
parser.add_argument("--month", help="Month", type=int, required=True)
args = parser.parse_args()

# Check moose availability
if not moose.has_moose_support():
    raise Exception("Moose unavailable")
if not moose.check_moose_commands_enabled(moose.MOOSE_LS):
    raise Exception("'moo ls' disabled")
if not moose.check_moose_commands_enabled(moose.MOOSE_PUT):
    raise Exception("'moo put' disabled")

# Base location for storage
mbase = "moose:/adhoc/users/philip.brohan"
moose_dir = "%s/opfc/ERA5/hourly/%04d" % (mbase, args.year)
if moose.run_moose_command("moo test %s" % moose_dir)[0] != "true":
    # Make the moose directory
    moose.run_moose_command("moo mkdir -p %s" % moose_dir)

# Disc data dir
ddir = "%s/opfc/ERA5/hourly/%04d" % (os.environ["SCRATCH"], args.year)

# Already done?
if (
    moose.run_moose_command("moo test -f %s/%02d.tar" % (moose_dir, args.month))[0]
    == "true"
):
    raise Exception("%04d-%02d already archived" % (args.year, args.month))

# Are there any fields to archive?
ofiles = glob.glob("%s/%02d/*.nc" % (ddir, args.month))
if len(ofiles) == 0:  # No fields on disc
    raise Exception("No files on disc for %04d-%02d" % (args.year, args.month))

# Pack the month's fields into a single file
otarf = "%s/%02d.tar" % (ddir, args.month)
tf = tarfile.open(name=otarf, mode="w")
blen = len(ddir)
for of in ofiles:
    tf.add(of, arcname=of[blen:])
tf.close()

# Stow the ob file on MASS
moose.put(ddir, [otarf], moose_dir)

# Clean up
os.remove(otarf)

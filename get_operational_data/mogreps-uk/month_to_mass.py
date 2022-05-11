#!/usr/bin/env python

# Archive downloaded mogreps-uk data to MASS
# Batched up as 1 months data for a given range of lead times

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
if not moose.check_moose_commands_enabled(moose.MOOSE_PUT):
    raise Exception("'moo put' disabled")

# Base location for storage
mbase = "moose:/adhoc/users/philip.brohan"
moose_dir = "%s/opfc/mogreps-uk/%04d" % (mbase, args.year)
if moose.run_moose_command("moo test %s" % moose_dir)[0] != "true":
    # Make the moose directory
    moose.run_moose_command("moo mkdir -p %s" % moose_dir)

# Disc data dir
ddir = "%s/opfc/mogreps-uk/%04d" % (os.environ["SCRATCH"], args.year)

# Already done?
if (
    moose.run_moose_command(
        "moo test -f %s/%02d_%03d_%03d.tar"
        % (moose_dir, args.month, args.min_lead, args.max_lead)
    )[0]
    == "true"
):
    raise Exception(
        "%04d-%02d lead %03d to %03d already archived"
        % (args.year, args.month, args.min_lead, args.max_lead)
    )

# Are there any fields to archive?
ofiles = glob.glob(
    "%s/%02d/*/*_%03d_%03d_*.pp" % (ddir, args.month, args.min_lead, args.max_lead)
)
if len(ofiles) == 0:  # No fields on disc
    raise Exception(
        "No files on disc for %04d-%02d lead %03d to %03d"
        % (args.year, args.month, args.min_lead, args.max_lead)
    )

# Pack the month's fields into a single file
otarf = "%s/%02d_%03d_%03d.tar" % (ddir, args.month, args.min_lead, args.max_lead,)
tf = tarfile.open(name=otarf, mode="w")
blen = len(ddir)
for of in ofiles:
    tf.add(of, arcname=of[blen:])
tf.close()

# Stow the ob file on MASS
moose.put(ddir, [otarf], moose_dir)

# Clean up
os.remove(otarf)

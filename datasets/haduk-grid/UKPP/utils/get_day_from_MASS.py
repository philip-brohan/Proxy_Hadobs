#!/usr/bin/env python

# Get UKPP fields for 1 day from MASS, and store on SCRATCH.

import os
import afterburner.io.moose2 as moose
import tarfile
import subprocess
import glob

# Check moose availability
if not moose.has_moose_support():
    raise Exception("Moose unavailable")
if not moose.check_moose_commands_enabled(moose.MOOSE_LS):
    raise Exception("'moo ls' disabled")
if not moose.check_moose_commands_enabled(moose.MOOSE_GET):
    raise Exception("'moo get' disabled")

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--year", type=int, required=True)
parser.add_argument("--month", type=int, required=True)
parser.add_argument("--day", type=int, required=True)
args = parser.parse_args()

moose_dir = "moose:/opfc/atm/postpro/prods/%04d.tar" % args.year

local_dir = "%s/Proxy_Hadobs/opfc/UKPP/%04d%02d%02d" % (
    os.getenv("SCRATCH"),
    args.year,
    args.month,
    args.day,
)
if not os.path.isdir(local_dir):
    os.makedirs(local_dir)


def unarchive(year, month, day):
    for hour in range(0, 24):
        tar_file = "%s/%04d%02d%02dT%02d30Z_UKP.tar" % (
            local_dir,
            year,
            month,
            day,
            hour,
        )
        if os.path.isfile(tar_file):
            continue
        try:
            moose.get(
                os.path.dirname(tar_file),
                "%s/%s" % (moose_dir, os.path.basename(tar_file)),
            )
        except Exception as e:
            print(e)
            print(
                "Failed to retrieve data for %04d-%02d-%02d:%02d"
                % (year, month, day, hour)
            )
            continue


unarchive(args.year, args.month, args.day)

#!/usr/bin/env python

# Get Improver UK fields for from MASS, and store on SCRATCH.

import os
import sys
import afterburner.io.moose2 as moose

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
parser.add_argument("--hour", type=int, required=False, default=None)
args = parser.parse_args()

moose_dir = "moose:/adhoc/users/christopher.sampson/"

local_dir = "%s/Proxy_Hadobs/opfc/Improver/%04d%02d%02d" % (
    os.getenv("SCRATCH"),
    args.year,
    args.month,
    args.day,
)
if not os.path.isdir(local_dir):
    os.makedirs(local_dir)


def unarchive(year, month, day, hr):
    for hour in range(0, 24):
        if hr is not None and hr != hour:
            continue
        lhdir = "%s/mix_suite_%04d%02d%02dT%02d00Z" % (
            local_dir,
            year,
            month,
            day,
            hour,
        )
        if not os.path.isdir(lhdir):
            os.makedirs(lhdir)
        mhdir = "%s/mix_suite_%04d%02d%02dT%02d00Z" % (
            moose_dir,
            year,
            month,
            day,
            hour,
        )
        tar_file = "%s/grid.tar" % lhdir
        if os.path.isfile(tar_file):
            continue
        try:
            moose.get(
                os.path.dirname(tar_file),
                "%s/%s" % (mhdir, os.path.basename(tar_file)),
            )
        except Exception as e:
            print(e)
            print(
                "Failed to retrieve data for %04d-%02d-%02d:%02d"
                % (year, month, day, hour)
            )
            continue


unarchive(args.year, args.month, args.day, args.hour)

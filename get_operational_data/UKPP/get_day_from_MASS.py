#!/usr/bin/env python

# Get UKPP fields for 1 day from MASS, and store on SCRATCH.

import os
import afterburner.io.moose2 as moose
import tarfile
import subprocess

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
        moose.get(
            os.path.dirname(tar_file), "%s/%s" % (moose_dir, os.path.basename(tar_file))
        )
        tf = tarfile.open(tar_file)
        tf.extractall(path=local_dir)
    # Uncompress the data we want, delete the rest
    nfiles = os.listdir("%s" % local_dir)
    for nfile in nfiles:
        # if nfile[-4:] == '.tar':
        #    continue
        if nfile[-17:] == "temperature_2km.Z":
            pret = subprocess.run("uncompress %s/%s" % (local_dir, nfile), shell=True)
            pret.check_returncode()
        else:
            os.remove("%s/%s" % (local_dir, nfile))


unarchive(args.year, args.month, args.day)

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


def hour_is_done(year, month, day, hour):
    hr_file = "%s/%04d%02d%02d%02d00_u1096_ng_pp_temperature_2km" % (
        local_dir,
        year,
        month,
        day,
        hour,
    )
    if os.path.isfile(hr_file):
        return True
    return False


def unarchive(year, month, day):
    for hour in range(0, 24):
        if hour_is_done(year, month, day, hour):
            continue
        tar_file = "%s/%04d%02d%02dT%02d30Z_UKP.tar" % (
            local_dir,
            year,
            month,
            day,
            hour,
        )
        if os.path.isfile(tar_file):
            os.remove(tar_file)
        try:
            moose.get(
                os.path.dirname(tar_file),
                "%s/%s" % (moose_dir, os.path.basename(tar_file)),
            )
            tf = tarfile.open(tar_file)
            tf.extractall(path=local_dir)
        except Exception:
            continue
    # Uncompress the data we want, delete the rest
    nfiles = os.listdir("%s" % local_dir)
    for nfile in nfiles:
        if nfile[-4:] == "_2km":
            continue
        if nfile[-17:] == "temperature_2km.Z":
            pret = subprocess.run("uncompress %s/%s" % (local_dir, nfile), shell=True)
            pret.check_returncode()
        else:
            os.remove("%s/%s" % (local_dir, nfile))
    # Reset the modification time -
    #     otherwise scratch will delete them.
    ofiles = glob.glob("%s/*" % local_dir)
    for ofile in ofiles:
        os.utime(ofile, None)


unarchive(args.year, args.month, args.day)

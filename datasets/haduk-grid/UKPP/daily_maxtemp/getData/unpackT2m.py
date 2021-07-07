#!/usr/bin/env python

# Unpack the temperature data from the UKPP tarfiles

import os
import tarfile
import subprocess
import glob


import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--year", type=int, required=True)
parser.add_argument("--month", type=int, required=True)
parser.add_argument("--day", type=int, required=True)
args = parser.parse_args()

local_dir = "%s/Proxy_Hadobs/opfc/UKPP/%04d%02d%02d" % (
    os.getenv("SCRATCH"),
    args.year,
    args.month,
    args.day,
)
if not os.path.isdir(local_dir):
    os.makedirs(local_dir)


def hour_file_name(year, month, day, hour):
    hr_file = "%04d%02d%02d%02d00_u1096_ng_pp_temperature_2km" % (
        year,
        month,
        day,
        hour,
    )
    return hr_file


# Extract the 2m temperatures
def unpack(year, month, day):
    for hour in range(0, 24):
        hfn = hour_file_name(year, month, day, hour)
        if os.path.isfile("%s/%s" % (local_dir, hfn)):
            continue
        tar_file = "%s/%04d%02d%02dT%02d30Z_UKP.tar" % (
            local_dir,
            year,
            month,
            day,
            hour,
        )
        if not os.path.isfile(tar_file):
            raise Exception(
                "UKPP data file not available, run the MASS extraction first"
            )
        if not os.path.isfile("%s/%s.Z" % (local_dir, hfn)):
            tf = tarfile.open(tar_file)
            tf.extract("%s.Z" % hfn, path=local_dir)
        # Uncompress the extracted data
        pret = subprocess.run(
            "uncompress %s/%s" % (local_dir, "%s.Z" % hfn), shell=True
        )
        pret.check_returncode()
    # Reset the modification time -
    #     otherwise scratch will delete them.
    ofiles = glob.glob("%s/*" % local_dir)
    for ofile in ofiles:
        os.utime(ofile, None)


unpack(args.year, args.month, args.day)

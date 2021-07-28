#!/usr/bin/env python

# Unpack the temperature data from the Improver tarfiles

import os
import tarfile

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--year", type=int, required=True)
parser.add_argument("--month", type=int, required=True)
parser.add_argument("--day", type=int, required=True)
args = parser.parse_args()

local_dir = "%s/Proxy_Hadobs/opfc/Improver" % (os.getenv("SCRATCH"),)
if not os.path.isdir(local_dir):
    os.makedirs(local_dir)


# Extract the 2m temperatures
def unpack(year, month, day):
    for hour in range(0, 24):
        tar_file = "%s/%04d%02d%02d/mix_suite_%04d%02d%02dT%02d00Z/grid.tar" % (
            local_dir,
            year,
            month,
            day,
            year,
            month,
            day,
            hour,
        )
        if not os.path.isfile(tar_file):
            print(
                "Data file not available: %s" % tar_file
            )
            continue
        try:
            tf = tarfile.open(tar_file)
            contents = tf.getmembers()
            for ct in contents:
                if (
                    "percentile_extract_" in ct.name
                    and "-temperature_at_screen_level.nc" in ct.name
                ):
                    ctdir = "%s/temperature_at_screen_level/%s/%s/%s/%s" % (
                        local_dir,
                        ct.name[21:25],
                        ct.name[25:27],
                        ct.name[27:29],
                        ct.name[30:32],
                    )
                    if not os.path.isdir(ctdir):
                        os.makedirs(ctdir)
                    if not os.path.isfile("%s/%s" % (ctdir, ct.name)):
                        tf.extract(ct, set_attrs=False, path=ctdir)
        except Exception as e:
            print(e)


unpack(args.year, args.month, args.day)

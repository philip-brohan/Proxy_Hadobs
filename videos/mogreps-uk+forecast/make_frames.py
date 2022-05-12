#!/usr/bin/env python

# Make all the individual frames for a movie

import os
import subprocess
import datetime

# Where to put the output files
opdir = "%s/slurm_output" % os.getenv("SCRATCH")
if not os.path.isdir(opdir):
    os.makedirs(opdir)

# Functions to check if the job is already done for this timepoint
def ncst_is_done(year, month, day, hour, minute):
    op_file_name = (
        "%s/images/opfc_mogreps_uk_3var_000_006/" + "%04d%02d%02d%02d%02d.png"
    ) % (os.getenv("SCRATCH"), year, month, day, hour, minute,)
    if os.path.isfile(op_file_name):
        return True
    return False


def fcst_is_done(year, month, day, hour, minute):
    op_file_name = (
        "%s/images/opfc_mogreps_uk_3var_120_126/" + "%04d%02d%02d%02d%02d.png"
    ) % (os.getenv("SCRATCH"), year, month, day, hour, minute,)
    if os.path.isfile(op_file_name):
        return True
    return False


def cmp_is_done(year, month, day, hour, minute):
    op_file_name = (
        "%s/images/opfc_mogreps_uk_3var_120_126/" + "%04d%02d%02d%02d%02d.png"
    ) % (os.getenv("SCRATCH"), year, month, day, hour, minute,)
    if (
        ncst_is_done(year, month, day, hour, minute)
        and fcst_is_done(year, month, day, hour, minute)
        and os.path.isfile(op_file_name)
    ):
        return True
    return False


f = open("run.txt", "w+")

start_day = datetime.datetime(2022, 1, 31, 0, 2)
end_day = datetime.datetime(2022, 2, 1, 23, 59)

current_day = start_day
while current_day <= end_day:
    cmd = ""
    if not ncst_is_done(
        current_day.year,
        current_day.month,
        current_day.day,
        current_day.hour,
        current_day.minute,
    ):
        cmd += (
            "../mogreps-uk/make_frame.py --year=%d --month=%d "
            + "--day=%d --hour=%d --minute=%d "
            + "--min_lead=0 --max_lead=6"
        ) % (
            current_day.year,
            current_day.month,
            current_day.day,
            current_day.hour,
            current_day.minute,
        )
    if not fcst_is_done(
        current_day.year,
        current_day.month,
        current_day.day,
        current_day.hour,
        current_day.minute,
    ):
        if len(cmd) > 0:
            cmd += "; "
        cmd += (
            "../mogreps-uk/make_frame.py --year=%d --month=%d "
            + "--day=%d --hour=%d --minute=%d "
            + "--min_lead=120 --max_lead=126 --no-label"
        ) % (
            current_day.year,
            current_day.month,
            current_day.day,
            current_day.hour,
            current_day.minute,
        )
    if not cmp_is_done(
        current_day.year,
        current_day.month,
        current_day.day,
        current_day.hour,
        current_day.minute,
    ):
        if len(cmd) > 0:
            cmd += "; "
        cmd += (
            "./make_frame.py --year=%d --month=%d " + "--day=%d --hour=%d --minute=%d"
        ) % (
            current_day.year,
            current_day.month,
            current_day.day,
            current_day.hour,
            current_day.minute,
        )
    if len(cmd) > 0:
        cmd += "\n"
        f.write(cmd)
    current_day = current_day + datetime.timedelta(minutes=10)
f.close()

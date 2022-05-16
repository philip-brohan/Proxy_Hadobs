#!/usr/bin/env python

# Composite forecast and analysis mogreps-uk plots into a single figure.
# Requires the individual plots to have been made already.

import os
import sys
from PIL import Image

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--year", help="Year", type=int, required=True)
parser.add_argument("--month", help="Integer month", type=int, required=True)
parser.add_argument("--day", help="Day of month", type=int, required=True)
parser.add_argument("--hour", help="Time of day (0 to 23)", type=int, required=True)
parser.add_argument(
    "--minute", help="Minute of hour (0 to 59)", type=int, required=True
)
parser.add_argument(
    "--opdir",
    help="Directory for output files",
    default="%s/images/opfc_mogreps_uk_3var_composite" % os.getenv("SCRATCH"),
    type=str,
    required=False,
)

args = parser.parse_args()
if not os.path.isdir(args.opdir):
    os.makedirs(args.opdir)

# Scale factor for sub images
sis = 0.65

# Create a background image
bg = Image.new("RGB", (3840, 2160), (256, 256, 256))

# Add the forecast image to the background
fcst = Image.open(
    "%s/images/opfc_mogreps_uk_3var_120_126/%04d%02d%02d%02d%02d.png"
    % (os.getenv("SCRATCH"), args.year, args.month, args.day, args.hour, args.minute)
)
fcst.thumbnail((int(2520 * sis), int(3270 * sis)), Image.ANTIALIAS)
bg.paste(fcst, (int((3840 - (2520 * sis) * 2) / 3), int((2160 - 3270 * sis) / 2)))

# Add the nowcast image to the background
ncst = Image.open(
    "%s/images/opfc_mogreps_uk_3var_000_006/%04d%02d%02d%02d%02d.png"
    % (os.getenv("SCRATCH"), args.year, args.month, args.day, args.hour, args.minute)
)
ncst.thumbnail((int(2520 * sis), int(3270 * sis)), Image.ANTIALIAS)
bg.paste(
    ncst,
    (
        int(((3840 - (2520 * sis) * 2) // 3) * 2 + int(2520 * sis)),
        int((2160 - 3270 * sis) // 2),
    ),
)


# Output the composite
bg.save(
    "%s/%04d%02d%02d%02d%02d.png"
    % (args.opdir, args.year, args.month, args.day, args.hour, args.minute,)
)

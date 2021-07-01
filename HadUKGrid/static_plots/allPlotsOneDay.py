#!/usr/bin/env python

# Make a full set of Tmax diagnostic plots for one day.

import argparse
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("--year", help="Year", type=int, required=True)
parser.add_argument("--month", help="Integer month", type=int, required=True)
parser.add_argument("--day", help="Day of month", type=int, required=True)
args = parser.parse_args()

for source in ("HadUKGrid", "UKPP"):
    for pType in ("actuals", "anomalies", "differences"):
        cp = subprocess.run(
            (
                "./plotMap.py --year=%02d --month=%04d --day=%02d"
                + " --source=%s --type=%s"
            )
            % (args.year, args.month, args.day, source, pType),
            shell=True,
            check=True,
        )


for pType in ("actuals", "anomalies", "differences"):
    cp = subprocess.run(
        ("./plotTS.py --year=%04d --month=%02d --day=%02d --type=%s")
        % (args.year, args.month, args.day, pType),
        shell=True,
        check=True,
    )

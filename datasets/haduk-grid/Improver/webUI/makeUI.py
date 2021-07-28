#!/usr/bin/env python

# Make a web page combining diagnostics for one day

import os
import sys
import argparse

sys.path.append("%s/./divs" % os.path.dirname(__file__))
from DateNav import divDateNav
from Map import divMap
from TS import divTS
from SelectPType import selectPType
from SelectLead import selectLead
from DocLinks import docLinks

parser = argparse.ArgumentParser()
parser.add_argument("--year", help="Year", type=int, required=True)
parser.add_argument("--month", help="Integer month", type=int, required=True)
parser.add_argument("--day", help="Day of month", type=int, required=True)
parser.add_argument(
    "--lead_time",
    help="Lead time in hours",
    choices=[0, 24, 48, 72, 96, 120, 144, 168],
    type=int,
    required=True,
)
parser.add_argument(
    "--variable",
    help="daily-maxtemp only",
    choices=["daily-maxtemp"],
    type=str,
    required=True,
)
parser.add_argument(
    "--adjustment",
    help="Adjustment algorithm",
    choices=["raw"],
    type=str,
    required=True,
)
parser.add_argument(
    "--opdir", help="Directory for output files", default=None, type=str, required=False
)
parser.add_argument(
    "--type",
    help="actuals, anomalies, or differences",
    choices=["actuals", "anomalies", "differences"],
    type=str,
    required=True,
)
args = parser.parse_args()

opdir = None
if args.opdir is None:
    opdir = "%s/Proxy_Hadobs/figures/haduk-grid/Improver/%s/%s/%04d/%02d/%02d" % (
        os.getenv("SCRATCH"),
        args.variable,
        args.adjustment,
        args.year,
        args.month,
        args.day,
    )
else:
    opdir = args.opdir

# Wrapped in try because we may make lots of pages in parallel and we can get a
#  race condition if two scripts both use the same opdir.
if not os.path.isdir(opdir):
    try:
        os.makedirs(opdir)
    except Exception:
        pass

fname = "%s/%s_%03d.html" % (opdir, args.type, args.lead_time)
fh = open(fname, "w")


# Create the main page contents with time-series and map plots
def divBody(fh, year, month, day, pType, lead_time):
    print("</body>\n", file=fh)
    print(
        (
            '<div class="document">\n'
            + '<div class="documentwrapper">\n'
            + '<div class="bodywrapper">\n'
            + '<div class="body" role="main">\n'
        ),
        file=fh,
    )
    title = "daily-maxtemp %s: %04d-%02d-%02d at %d hours forecast lead-time" % (
        pType,
        year,
        month,
        day,
        lead_time,
    )
    print(
        ('<div class="section" id="%s">\n' + "<h1>%s</h1>\n") % (title, title), file=fh
    )
    divTS(fh, pType, lead_time)
    divMap(fh, pType, lead_time)
    print("</div>\n</div>\n</div>\n</div>\n</div>\n", file=fh)
    print("</body>\n", file=fh)


# Create the sidebar with navigation and controls
def divSidebar(fh, pType, lead_time):
    print(
        (
            '<div class="sphinxsidebar" role="navigation" '
            + 'aria-label="main navigation">\n'
            + '<div class="sphinxsidebarwrapper">\n'
        ),
        file=fh,
    )
    # Controls for selecting if actuals, anomalies, ...
    selectPType(fh, pType, lead_time)
    # Controls for selecting lead-time
    selectLead(fh, pType, lead_time)
    # Link back to project documentation
    docLinks(fh)
    print(
        ("</div>\n" + "</div>\n"),
        file=fh,
    )


# Write the output
title = "Tmax %s for %04d-%02d-%02d" % (args.type, args.year, args.month, args.day)
print(
    (
        "\n<!DOCTYPE html>\n"
        + '<html xmlns="http://www.w3.org/1999/xhtml">\n'
        + "<head>\n"
        + '<meta charset="utf-8" />\n'
        + "<title>%s</title>\n"
        + '<link rel="stylesheet" href="../../../../../../../_static/sphinxdoc.css"'
        + '   type="text/css" />\n'
        + '<link rel="stylesheet" href="../../../../../../../_static/pygments.css"'
        + '   type="text/css" />\n'
        + "</head>\n"
    )
    % title,
    file=fh,
)
divDateNav(fh, args.year, args.month, args.day, args.type, args.lead_time)
divSidebar(fh, args.type, args.lead_time)
divBody(fh, args.year, args.month, args.day, args.type, args.lead_time)
print("</html>\n", file=fh)

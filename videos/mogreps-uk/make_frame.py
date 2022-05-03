#!/usr/bin/env python

# Atmospheric state - near-surface temperature, wind, and precip.
# Scaled wind speed version

import os
import sys
import datetime

import iris
import numpy as np

import warnings

warnings.filterwarnings("ignore", message=".*keyword argument to TransverseMercator")

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
import cmocean
from pandas import qcut

sys.path.append("%s/../../get_operational_data/mogreps-uk" % os.path.dirname(__file__))
from MUK_load import load_mean

sys.path.append("%s/." % os.path.dirname(__file__))
# from plots import quantile_normalise_t2m
from plots import plot_cube
from plots import make_wind_seed
from plots import wind_field
from plots import get_precip_colours

# from plots import draw_lat_lon

# Fix dask SPICE bug
import dask

dask.config.set(scheduler="single-threaded")

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
    default="%s/images/opfc_mogreps_uk_3var_emean_analysis" % os.getenv("SCRATCH"),
    type=str,
    required=False,
)

args = parser.parse_args()
if not os.path.isdir(args.opdir):
    os.makedirs(args.opdir)

dte = datetime.datetime(args.year, args.month, args.day, args.hour, args.minute)

# Pole position
pole_latitude = 37.5
pole_longitude = 177.5
npg_longitude = 0
# Region to plot (degrees, rotated)
xmin = 355
xmax = 363
ymin = -3.76
ymax = 7.14

# In the  temperature field, damp the diurnal cycle, and
#  boost the short-timescale variability. Load the
#  recent data to calculate this.
# (tavg,davg) = load_recent_temperatures(dte)

# Load the model data
t2m = load_mean("air.2m", dte, max_members=10, max_lead=6)
# Remove the diurnal cycle
# t2m.data -= davg.data
# Double the synoptic variability
# t2m.data += (t2m.data-tavg.data)*1
# Add back a reduced diurnal cycle
# t2m.data += davg.data*0.25

u10m = load_mean("uwnd.10m", dte, max_members=10, max_lead=6)
v10m = load_mean("vwnd.10m", dte, max_members=10, max_lead=6)

# Smooth precip in time to blur ensemble member changes at the hour.
rain = load_mean("rain", dte, max_members=10, max_lead=6)
snow = load_mean("snow", dte, max_members=10, max_lead=6)
precip = rain + snow
dte_f = dte + datetime.timedelta(minutes=5)
p2 = load_mean("rain", dte_f, max_members=10, max_lead=6) + load_mean(
    "snow", dte_f, max_members=10, max_lead=6
)
dte_p = dte - datetime.timedelta(minutes=5)
p3 = load_mean("rain", dte_p, max_members=10, max_lead=6) + load_mean(
    "snow", dte_p, max_members=10, max_lead=6
)
precip = (precip + p2 + p3) / 3

mask = iris.load_cube(
    "%s/fixed_fields/land_mask/HadUKG_land_from_Copernicus.nc" % os.getenv("DATADIR")
)


# Define the figure (page size, background color, resolution, ...
fig = Figure(
    figsize=(8.4, 10.9),  # Width, Height (inches)
    dpi=300,
    facecolor=(0.5, 0.5, 0.5, 1),
    edgecolor=None,
    linewidth=0.0,
    frameon=False,  # Don't draw a frame
    subplotpars=None,
    tight_layout=None,
)
fig.set_frameon(False)
# Attach a canvas
canvas = FigureCanvas(fig)

# Make the wind noise
wind_pc = plot_cube(
    0.015, xmin, xmax, ymin, ymax, pole_latitude, pole_longitude, npg_longitude
)
cs = iris.coord_systems.RotatedGeogCS(pole_latitude, pole_longitude, npg_longitude)
rw = iris.analysis.cartography.rotate_winds(u10m, v10m, cs)
u10m = rw[0].regrid(wind_pc, iris.analysis.Linear())
v10m = rw[1].regrid(wind_pc, iris.analysis.Linear())
seq = (dte - datetime.datetime(2000, 1, 1)).total_seconds() / 60  # Minutes since
z = make_wind_seed(
    plot_cube(
        0.015, xmin, xmax, ymin, ymax, pole_latitude, pole_longitude, npg_longitude
    ),
    seed=1,
)
wind_noise_field = wind_field(
    u10m, v10m, z, sequence=int(seq / 5) * 5, epsilon=0.0005, iterations=50
)
# Smooth out the field where the wind speed is low.
# (Highlights temperature variability and reduces visual artefacts).
ws = iris.analysis.maths.apply_ufunc(np.sqrt,v10m*v10m+u10m*u10m)
wind_noise_field *= iris.analysis.maths.apply_ufunc(np.sqrt,ws)/3

# Define an axes to contain the plot. In this case our axes covers
#  the whole figure
ax = fig.add_axes([0, 0, 1, 1])
ax.set_axis_off()  # Don't want surrounding x and y axis

# Lat and lon range (in rotated-pole coordinates) for plot
ax.set_xlim(xmin, xmax)
ax.set_ylim(ymin, ymax)
ax.set_aspect("auto")

# Background
ax.add_patch(
    Rectangle(
        (xmin, ymin),
        xmax - xmin,
        ymax - ymin,
        facecolor=(0.6, 0.6, 0.6, 1),
        fill=True,
        zorder=1,
    )
)

# Plot the land mask
mask_pc = plot_cube(
    0.01, xmin, xmax, ymin, ymax, pole_latitude, pole_longitude, npg_longitude
)
mask = mask.regrid(mask_pc, iris.analysis.Nearest())
lats = mask.coord("latitude").points
lons = mask.coord("longitude").points
mask_img = ax.pcolorfast(
    lons,
    lats,
    mask.data,
    cmap=matplotlib.colors.ListedColormap(((0.4, 0.4, 0.4, 0), (0.4, 0.4, 0.4, 0.3))),
    vmin=0,
    vmax=1,
    alpha=1.0,
    zorder=700,
)


# Plot the T2M
t2m_pc = plot_cube(
    0.01, xmin, xmax, ymin, ymax, pole_latitude, pole_longitude, npg_longitude
)
t2m = t2m.regrid(t2m_pc, iris.analysis.Linear())

# Plot as a colour map
wnf = wind_noise_field.regrid(t2m, iris.analysis.Linear())

t2m_img = ax.pcolorfast(
    lons,
    lats,
    t2m.data + wnf.data / 10,
    cmap=cmocean.cm.balance,
    vmin=270 - 1,
    vmax=290 + 1,
    alpha=1.0,
    zorder=100,
)

# Plot the precip
precip = precip.regrid(t2m_pc, iris.analysis.Linear())
precip.data[precip.data > 0.001] = 0.001

wnf = wind_noise_field.regrid(precip, iris.analysis.Linear())
precip.data *= 1 + wnf.data / 40
precip.data = np.ma.masked_where(precip.data < 2.0e-4, precip.data)
precip_img = ax.pcolorfast(
    lons, lats, precip.data, cmap=cmocean.cm.rain, vmin=-0.0005, vmax=0.0017, zorder=200
)

# Label with the date
ax.text(
    xmax - (xmax - xmin) * 0.021,
    ymax - (ymax - ymin) * 0.016,
    "%04d-%02d-%02d:%02d" % (args.year, args.month, args.day, args.hour),
    horizontalalignment="right",
    verticalalignment="top",
    color="black",
    bbox=dict(
        facecolor=(0.6, 0.6, 0.6, 0.5), edgecolor="black", boxstyle="round", pad=0.2
    ),
    size=14,
    clip_on=True,
    zorder=500,
)

# Render the figure as a png
fig.savefig(
    "%s/%04d%02d%02d%02d%02d.png"
    % (args.opdir, args.year, args.month, args.day, args.hour, args.minute,)
)

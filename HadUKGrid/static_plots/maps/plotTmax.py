#!/usr/bin/env python

# Plot HadUKGrid Tmax

import os
import numpy as np

import iris
import iris.analysis

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.lines import Line2D

import cmocean


def plotTmax(
    field,
    vMax=None,
    vMin=None,
    latMax=1250,
    latMin=-200,
    lonMax=700,
    lonMin=-200,
    height=11 * 1.61,
    width=11,
    opDir=None,
    fName=None,
    lMask=None,
):

    # Set the defaults
    if opDir is None:
        opDir = "."
    if fName is None:
        fName = "TMax.png"
    if vMax is None:
        vMax = np.max(field.data)
    if vMin is None:
        vMin = np.min(field.data)
    if lMask is None:
        lMask = iris.load_cube(
            "%s/fixed_fields/land_mask/HadUKG_land_from_Copernicus.nc"
            % os.getenv("DATADIR")
        )

    fig = Figure(
        figsize=(width, height),
        dpi=100,
        facecolor=(0.5, 0.5, 0.5, 1),
        edgecolor=None,
        linewidth=0.0,
        frameon=False,
        subplotpars=None,
        tight_layout=None,
    )
    canvas = FigureCanvas(fig)
    font = {
        "family": "sans-serif",
        "sans-serif": "Arial",
        "weight": "normal",
        "size": 16,
    }
    matplotlib.rc("font", **font)
    axb = fig.add_axes([0, 0, 1, 1])

    # Axes for the map
    ax_map = fig.add_axes([0.075, 0.055, 0.9, 0.95])
    # ax_map.set_axis_off()
    ax_map.set_ylim(latMin, latMax)
    ax_map.set_xlim(lonMin, lonMax)
    # Centre on page with aspect ratio from data
    ax_map.set_aspect("equal", adjustable="box", anchor="C")

    # Land mask
    lMask = lMask.regrid(field, iris.analysis.Nearest())
    lats = lMask.coord("projection_y_coordinate").points / 1000
    lons = lMask.coord("projection_x_coordinate").points / 1000
    mask_img = ax_map.pcolorfast(
        lons,
        lats,
        lMask.data,
        cmap=matplotlib.colors.ListedColormap(((0.7, 0.7, 0.7, 1), (0.4, 0.4, 0.4, 1))),
        vmin=0,
        vmax=1,
        alpha=1.0,
        zorder=20,
    )

    # Temperatures
    T_img = ax_map.pcolorfast(
        lons,
        lats,
        field.data,
        cmap=cmocean.cm.balance,
        vmin=vMin,
        vmax=vMax,
        alpha=0.8,
        zorder=40,
    )

    # ColourBar
    ax_cb = fig.add_axes([0.075, 0.0, 0.9, 0.05])
    ax_cb.set_axis_off()
    cb = fig.colorbar(
        T_img, ax=ax_cb, location="bottom", orientation="horizontal", fraction=1.0
    )

    if not os.path.isdir(opDir):
        os.makedirs(opDir)

    # Output as png
    fig.savefig("%s/%s" % (opDir, fName))

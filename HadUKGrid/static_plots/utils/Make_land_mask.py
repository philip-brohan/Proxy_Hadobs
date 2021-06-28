#!/usr/bin/env python

# Make a land-mask on the HadUK Grid

import os
import sys
import numpy as np

import iris
import iris.analysis

sys.path.append("%s/." % os.path.dirname(__file__))
from HUKG_load_tmax import HUKG_load_tmax


coord_s = iris.coord_systems.GeogCS(iris.fileformats.pp.EARTH_RADIUS)
lct = iris.load_cube(
    ("/data/users/hadpb/fixed_fields/land_use/"+
     "PROBAV_LC100_global_v3.0.1_2019-nrt_Discrete-Classification-map_EPSG-4326.nc"),
    iris.Constraint(latitude=lambda cell: 47 < cell < 61)
    & iris.Constraint(longitude=lambda cell: -15 < cell < 5),
)
lct.data[lct.data == 200] = 0
lct.data[lct.data != 0] = 1
lct.coord("latitude").coord_system = coord_s
lct.coord("longitude").coord_system = coord_s

# Load the HadUKGrid data
hdata = HUKG_load_tmax(2021,3,12)

mask = lct.regrid(hdata,iris.analysis.Nearest())

iris.save(mask,'HadUKG_land_from_Copernicus.nc')


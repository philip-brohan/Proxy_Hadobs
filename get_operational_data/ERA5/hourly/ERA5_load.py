# Functions to load ERA5 data

import os
import iris
import iris.cube
import iris.time
import iris.coord_systems
import iris.fileformats
import datetime

# Need to add coordinate system metadata so they work with cartopy
coord_s = iris.coord_systems.GeogCS(iris.fileformats.pp.EARTH_RADIUS)


def load_hourly_at_hour(variable, year, month, day, hour):
    fname = "%s/opfc/ERA5/hourly/%04d/%02d/%s.nc" % (
        os.getenv("SCRATCH"),
        year,
        month,
        variable,
    )
    if not os.path.isfile(fname):
        raise Exception("No data file %s" % fname)
    ftt = iris.Constraint(
        time=iris.time.PartialDateTime(year=year, month=month, day=day, hour=hour)
    )
    hslice = iris.load_cube(fname, ftt)
    hslice.coord("latitude").coord_system = coord_s
    hslice.coord("longitude").coord_system = coord_s
    return hslice


def load_hourly(variable, validity_time):
    """Load requested ensemble mean data from disc, interpolating if necessary.
    """
    ptime = datetime.datetime(
        validity_time.year,
        validity_time.month,
        validity_time.day,
        validity_time.hour,
        0,
    )
    if ptime == validity_time:
        return load_hourly_at_hour(
            variable,
            validity_time.year,
            validity_time.month,
            validity_time.day,
            validity_time.hour,
        )
    s_previous = load_hourly_at_hour(
        variable, ptime.year, ptime.month, ptime.day, ptime.hour
    )
    ntime = ptime + datetime.timedelta(hours=1)
    s_next = load_hourly_at_hour(
        variable, ntime.year, ntime.month, ntime.day, ntime.hour
    )

    # Iris won't merge cubes with different attributes
    s_previous.attributes = s_next.attributes
    s_next = iris.cube.CubeList((s_previous, s_next)).merge_cube()
    s_next = s_next.interpolate([("time", validity_time)], iris.analysis.Linear())
    return s_next

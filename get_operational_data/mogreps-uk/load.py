# Functions to load mogreps-uk data

import os
import iris
import iris.cube
import iris.time
import iris.fileformats
import iris.util
import cf_units
import datetime
import glob
import numpy as np

# Variable name to iris stash code
#  See https://code.metoffice.gov.uk/trac/nwpscience/wiki/ModelInfo
def stash_from_variable_names(variable):
    if variable == "prmsl":
        return iris.fileformats.pp.STASH(1, 16, 222)
    if variable == "air.2m":
        return iris.fileformats.pp.STASH(1, 3, 236)
    if variable == "uwnd.10m":
        return iris.fileformats.pp.STASH(1, 3, 225)
    if variable == "vwnd.10m":
        return iris.fileformats.pp.STASH(1, 3, 226)
    if variable == "rain":
        return iris.fileformats.pp.STASH(1, 4, 203)
    if variable == "snow":
        return iris.fileformats.pp.STASH(1, 4, 204)
    raise Exception("Unsupported variable %s" % variable)


# File names for data for a given validity_time
def get_file_names(ftime):
    data_dir = "%s/opfc/mogreps-uk/%04d/%02d/%02d" % (
        os.getenv("SCRATCH"),
        ftime.year,
        ftime.month,
        ftime.day,
    )
    fl = glob.glob("%s/%02d_*.pp" % (data_dir, ftime.hour))
    return fl


def filter_files_by_lead(file_names, min_lead, max_lead):
    ff = []
    for fn in file_names:
        f_min_lead = int(fn[-12:-9])
        f_max_lead = int(fn[-8:-5])
        if (max_lead is None or max_lead >= f_min_lead) and (
            min_lead is None or min_lead <= f_max_lead
        ):
            ff.append(fn)
    return ff


def get_file_times(variable, validity_time):
    """Get the times for which data are available, needed to interpolate
        the data at the given validity time.
    Will be one time (=validity time) if the data for the requested time
     are on disc., and two times (closest previous time on disc and closest
     subsequent time on disc) otherwise."""
    if variable == "rain" or variable == "snow":
        if validity_time.minute % 5 == 0:
            return [validity_time]
        else:
            prevt = validity_time - datetime.timedelta(validity_time.minute % 5)
            return [prevt, prevt + datetime.timedelta(minutes=5)]
    else:
        if validity_time.minute == 0:
            return [validity_time]
        else:
            prevt = validity_time - datetime.timedelta(minutes=validity_time.minute)
            return [prevt, prevt + datetime.timedelta(hours=1)]


# Restore a length 1 first dimension to a cube which has been inappropriately squeezed.
# The parameters must exactly match any other cube you want to concatenate to.
def unsqueeze(
    cb,  # cube to unsqueeze
    dim_name="realization",  # Name of new dimension to add
    dim_value=np.int32(0),  # Value of single point in new dimension
    dim_units="1",  # Units of dimension
    promotable_scalars=[
        "forecast_period",
        "forecast_reference_time",
    ],  # Scalar coordinates which actually vary with the new dimension
):
    cb.add_aux_coord(
        iris.coords.AuxCoord(dim_value, standard_name=dim_name, units=dim_units)
    )
    cb = iris.util.new_axis(cb, dim_name)
    for acn in promotable_scalars:
        scrd = cb.coords(acn)[0]
        tpcrd = iris.coords.AuxCoord(
            scrd.points,
            standard_name=scrd.standard_name,
            long_name=scrd.long_name,
            var_name=scrd.var_name,
            units=scrd.units,
            attributes=scrd.attributes,
            coord_system=scrd.coord_system,
            climatological=scrd.climatological,
        )
        cb.remove_coord(acn)
        cb.add_aux_coord(tpcrd, 0)
    return cb


# Iris will seperate out any data from ensemble member 0 into independent cubes
#  (PP file format peculiarity). So we might get one cube, or several. Batch
#  them up into a single cube.
def ensemble_cube_up(cl):  # Input is a cube list
    if len(cl) == 1:
        return cl[0]
    for i, cb in enumerate(cl):
        if len(cb.data.shape) == 2:  # No realization dimension
            cl[i] = unsqueeze(cb)
    return cl.concatenate_cube()


def get_variable_at_ftime(variable, validity_time, min_lead=None, max_lead=None):
    """Get cube with the data, given that the validity time
    matches a data timestep. """
    file_names = filter_files_by_lead(get_file_names(validity_time), min_lead, max_lead)
    if len(file_names) == 0:
        raise Exception("Data not available")
    if max_lead is None:
        max_lead = 200
    if min_lead is None:
        min_lead = 0
    ftco = iris.Constraint(forecast_period=lambda t: t >= min_lead and t <= max_lead)
    if variable == "rain" or variable == "snow":
        ftt = iris.Constraint(
            time=iris.time.PartialDateTime(
                hour=validity_time.hour, minute=validity_time.minute
            )
        )
    else:
        ftt = iris.Constraint(time=iris.time.PartialDateTime(hour=validity_time.hour))
    stco = iris.AttributeConstraint(STASH=stash_from_variable_names(variable))
    hslice = iris.load(file_names, stco & ftco & ftt)
    hslice = ensemble_cube_up(hslice)
    return hslice


def load(variable, validity_time, max_lead=None, min_lead=None):
    """Load requested data from disc, interpolating if necessary.
    """
    ftimes = get_file_times(variable, validity_time)
    if len(ftimes) == 1:
        return get_variable_at_ftime(variable, ftimes[0], max_lead=None, min_lead=None)
    s_previous = get_variable_at_ftime(
        variable, ftimes[0], max_lead=None, min_lead=None
    )
    s_next = get_variable_at_ftime(variable, ftimes[1], max_lead=None, min_lead=None)

    # Iris won't merge cubes with different attributes
    s_previous.attributes = s_next.attributes
    s_next = iris.cube.CubeList((s_previous, s_next)).merge_cube()
    s_next = s_next.interpolate([("time", validity_time)], iris.analysis.Linear())
    return s_next

# Functions to load mogreps-uk data

import os
import iris
import iris.time
import datetime
import glob

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


def filter_files_by_lead(file_names, max_lead, min_lead):
    ff = []
    for fn in file_names:
        f_min_lead = int(fn[-12:-9])
        f_max_lead = int(fn[-8:-5])
        if (max_lead is None or max_lead <= f_max_lead) and (
            min_lead is None or min_lead >= f_min_lead
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


def get_variable_at_ftime(variable, validity_time, max_lead=None, min_lead=None):
    """Get cube with the data, given that the validity time
    matches a data timestep. """
    file_names = filter_files_by_lead(get_file_names(validity_time), max_lead, min_lead)
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
    hslice = iris.load_cube(file_names, stco & ftco & ftfr)
    return hslice

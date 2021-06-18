# Load daily tmax data from HadUKGrid

import iris


def HUKG_load_tmax(year, month, day):
    dirname = (
        "/data/users/haduk/uk_climate_data/supported/haduk-grid/series_archive_provisional/grid/daily_maxtemp/%04d/%02d"
        % (year, month)
    )
    filename = "%02d.nc" % day
    hdata = iris.load_cube("%s/%s" % (dirname, filename))
    return hdata

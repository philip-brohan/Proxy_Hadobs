# Load daily tmax data from HadUKGrid

import iris
import calendar
import datetime


def HUKG_load_tmax(args):
    dirname = (
        "/data/users/haduk/uk_climate_data/supported/haduk-grid/"
        + "series_archive_provisional/grid/daily_maxtemp/%04d/%02d"
    ) % (args.year, args.month)
    filename = "%02d.nc" % args.day
    hdata = iris.load_cube(
        "%s/%s" % (dirname, filename),
        iris.Constraint(
            projection_y_coordinate=lambda cell: args.latMin * 1000
            <= cell
            <= args.latMax * 1000
        )
        & iris.Constraint(
            projection_x_coordinate=lambda cell: args.lonMin * 1000
            <= cell
            <= args.lonMax * 1000
        ),
    )
    return hdata


# Get an approximate daily climatology from the HadUKGrid monthlies
def HUKG_load_tmax_climatology(args):
    dirname = (
        "/data/users/haduk/uk_climate_data/supported/haduk-grid/v1.0.3.0/"
        + "data/grid_archives/lta_archive_v1/grid/monthly_maxtemp_climatology/"
        + "1981-2010/"
    )
    if args.day == 15:
        filename = "%s.nc" % calendar.month_abbr[args.month].lower()
        hdata = iris.load_cube(
            "%s/%s" % (dirname, filename),
            iris.Constraint(
                projection_y_coordinate=lambda cell: args.latMin * 1000
                <= cell
                <= args.latMax * 1000
            )
            & iris.Constraint(
                projection_x_coordinate=lambda cell: args.lonMin * 1000
                <= cell
                <= args.lonMax * 1000
            ),
        )
    elif args.day < 15:
        dte = datetime.date(args.year, args.month, args.day)
        dt2 = datetime.date(args.year, args.month, 15)
        dt1 = dt2 - datetime.timedelta(days=30)
        dt1 = datetime.date(dt1.year, dt1.month, 15)
        fn1 = "%s.nc" % calendar.month_abbr[dt1.month].lower()
        hdata = iris.load_cube(
            "%s/%s" % (dirname, fn1),
            iris.Constraint(
                projection_y_coordinate=lambda cell: args.latMin * 1000
                <= cell
                <= args.latMax * 1000
            )
            & iris.Constraint(
                projection_x_coordinate=lambda cell: args.lonMin * 1000
                <= cell
                <= args.lonMax * 1000
            ),
        )
        fn2 = "%s.nc" % calendar.month_abbr[dt2.month].lower()
        hd2 = iris.load_cube(
            "%s/%s" % (dirname, fn2),
            iris.Constraint(
                projection_y_coordinate=lambda cell: args.latMin * 1000
                <= cell
                <= args.latMax * 1000
            )
            & iris.Constraint(
                projection_x_coordinate=lambda cell: args.lonMin * 1000
                <= cell
                <= args.lonMax * 1000
            ),
        )
        weight = (dt2 - dte).total_seconds() / (dt2 - dt1).total_seconds()
        hdata.data = hdata.data * weight + hd2.data * (1 - weight)
    else:
        dte = datetime.date(args.year, args.month, args.day)
        dt1 = datetime.date(args.year, args.month, 15)
        dt2 = dt1 + datetime.timedelta(days=30)
        dt2 = datetime.date(dt2.year, dt2.month, 15)
        fn1 = "%s.nc" % calendar.month_abbr[dt1.month].lower()
        hdata = iris.load_cube(
            "%s/%s" % (dirname, fn1),
            iris.Constraint(
                projection_y_coordinate=lambda cell: args.latMin * 1000
                <= cell
                <= args.latMax * 1000
            )
            & iris.Constraint(
                projection_x_coordinate=lambda cell: args.lonMin * 1000
                <= cell
                <= args.lonMax * 1000
            ),
        )
        fn2 = "%s.nc" % calendar.month_abbr[dt2.month].lower()
        hd2 = iris.load_cube(
            "%s/%s" % (dirname, fn2),
            iris.Constraint(
                projection_y_coordinate=lambda cell: args.latMin * 1000
                <= cell
                <= args.latMax * 1000
            )
            & iris.Constraint(
                projection_x_coordinate=lambda cell: args.lonMin * 1000
                <= cell
                <= args.lonMax * 1000
            ),
        )
        weight = (dt2 - dte).total_seconds() / (dt2 - dt1).total_seconds()
        hdata.data = hdata.data * weight + hd2.data * (1 - weight)
    return hdata

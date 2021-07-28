import datetime


def divDateNav(fh, year, month, day, pType, lead_time):
    dte = datetime.date(year, month, day)
    dPrev = dte - datetime.timedelta(days=1)
    dNext = dte + datetime.timedelta(days=1)
    print(
        (
            '<div class="related" role="navigation" aria-label="related navigation">\n'
            + "<h3>Navigation</h3>\n"
            + "<ul>\n"
            + '<li class="right" >\n'
            + '<a href="../../../%04d/%02d/%02d/%s_%03d.html" title="Next day"\n'
            + ' accesskey="N">Next day</a> |</li>\n'
            + '<li class="right" >\n'
            + '<a href="../../../%04d/%02d/%02d/%s_%03d.html" title="Previous day"\n'
            + ' accesskey="P">Previous day</a> |</li>\n'
            + "</ul>\n"
            + "</div>\n"
        )
        % (
            dNext.year,
            dNext.month,
            dNext.day,
            pType,
            lead_time,
            dPrev.year,
            dPrev.month,
            dPrev.day,
            pType,
            lead_time,
        ),
        file=fh,
    )

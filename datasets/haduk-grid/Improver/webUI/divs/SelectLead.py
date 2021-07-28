def selectLead(fh, pType, lead_time):
    print(
        ("<h3>Change lead time (hours)</a></h3>\n" + '<ul class="current">\n'),
        file=fh,
    )
    for tLead in [0, 24, 48, 72, 96, 120, 144, 168]:
        if tLead == lead_time:
            print(
                (
                    '<li class="toctree-l1 current">'
                    + '<a class="current reference internal" href="#">'
                    + "%d</a></li>\n"
                )
                % tLead,
                file=fh,
            )
        else:
            print(
                (
                    '<li class="toctree-l1">'
                    + '<a class="reference internal" href="%s_%03d.html">'
                    + "%d</a></li>\n"
                )
                % (pType, tLead, tLead),
                file=fh,
            )
    print(
        "</ul>\n",
        file=fh,
    )

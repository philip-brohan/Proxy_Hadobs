def selectPType(fh, pType, lead_time):
    print(
        ("<h3>Change view</a></h3>\n" + '<ul class="current">\n'),
        file=fh,
    )
    if pType == "actuals":
        print(
            (
                '<li class="toctree-l1 current">'
                + '<a class="current reference internal" href="#">'
                + "Actuals</a></li>\n"
            ),
            file=fh,
        )
    else:
        print(
            (
                '<li class="toctree-l1">'
                + '<a class="reference internal" href="actuals_%03d.html">'
                + "Actuals</a></li>\n"
            )
            % lead_time,
            file=fh,
        )
    if pType == "anomalies":
        print(
            (
                '<li class="toctree-l1 current">'
                + '<a class="current reference internal" href="#">'
                + "Anomalies</a></li>\n"
            ),
            file=fh,
        )
    else:
        print(
            (
                '<li class="toctree-l1">'
                + '<a class="reference internal" href="anomalies_%03d.html">'
                + "Anomalies</a></li>\n"
            )
            % lead_time,
            file=fh,
        )
    if pType == "differences":
        print(
            (
                '<li class="toctree-l1 current">'
                + '<a class="current reference internal" href="#">'
                + "Differences</a></li>\n"
            ),
            file=fh,
        )
    else:
        print(
            (
                '<li class="toctree-l1">'
                + '<a class="reference internal" href="differences_%03d.html">'
                + "Differences</a></li>\n"
            )
            % lead_time,
            file=fh,
        )
    print(
        "</ul>\n",
        file=fh,
    )

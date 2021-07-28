def divTS(fh, pType, lead_time):
    print('<div class="figure align-center" id="idTS" style="width: 95%" >\n', file=fh)
    print(
        (
            '<a class="reference internal image-reference" '
            + 'href="./TS_%03d_%s.png"><img alt="%s boxplot timeseries" '
            + 'src="./TS_%03d_%s.png" style="width: 95%%;" /></a>\n'
        )
        % (
            lead_time,
            pType,
            pType,
            lead_time,
            pType,
        ),
        file=fh,
    )
    if pType == "differences":
        print(
            (
                '<p class="caption"><span class="caption-text">'
                + "Blue: haduk-grid anomalies, "
                + "Right: Improver differences from haduk-grid, "
                + "(daily boxplots of all grid-point values (C))."
                + "</span></p>\n"
            ),
            file=fh,
        )
    else:
        print(
            (
                '<p class="caption"><span class="caption-text">'
                + "Blue: haduk-grid %s, "
                + "Red: Improver %s, "
                + "(daily boxplots of all grid-point values (C))."
                + "</span></p>\n"
            )
            % (pType, pType),
            file=fh,
        )
    print("</div>\n", file=fh)

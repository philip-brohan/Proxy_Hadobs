def divMap(fh, pType, lead_time):
    print('<div class="figure align-center" id="idM" style="width: 95%" >\n', file=fh)
    hType = pType
    if pType == "differences":
        hType = "anomalies"
    print(
        (
            '<a class="reference internal image-reference" '
            + 'href="./haduk-grid_map_%03d_%s.png"><img alt="haduk-grid %s map" '
            + 'src="./haduk-grid_map_%03d_%s.png" style="width: 47%%;" /></a>\n'
        )
        % (lead_time, hType, hType, lead_time, hType),
        file=fh,
    )
    print(
        (
            '<a class="reference internal image-reference" '
            + 'href="./Improver_map_%03d_%s.png"><img alt="Improver %s map" '
            + 'src="./Improver_map_%03d_%s.png" style="width: 47%%;" /></a>\n'
        )
        % (lead_time, pType, pType, lead_time, pType),
        file=fh,
    )
    if pType == "differences":
        print(
            (
                '<p class="caption"><span class="caption-text">'
                + "Left: haduk-grid anomalies, "
                + "Right: Improver differences from haduk-grid, (both C)."
                + "</span></p>\n"
            ),
            file=fh,
        )
    else:
        print(
            (
                '<p class="caption"><span class="caption-text">'
                + "Left: haduk-grid %s, "
                + "Right: Improver %s, (both C)."
                + "</span></p>\n"
            )
            % (pType, pType),
            file=fh,
        )
    print("</div>\n", file=fh)

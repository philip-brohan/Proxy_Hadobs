def docLinks(fh):
    print(
        (
            '<h3><a href="system documentation">System documentation</a></h3>\n'
            + "<ul>\n"
            + '<li><a href="https://github.com/philip-brohan/Proxy_Hadobs"'
            + ' rel="nofollow">Github repository</a></li>\n'
            + "</ul>\n"
            + "<h3>Found a bug, or have a suggestion?</h3>\n"
            + ' Please <a href="https://github.com/philip-brohan/'
            + 'Proxy_Hadobs/issues/new">raise an issue</a>.\n'
            + "</div>\n"
            + "</div>\n"
        ),
        file=fh,
    )

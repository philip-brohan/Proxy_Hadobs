#!/usr/bin/env python

# Make a web page combining diagnostics for one day

parser = argparse.ArgumentParser()
parser.add_argument("--year", help="Year", type=int, required=True)
parser.add_argument("--month", help="Integer month", type=int, required=True)
parser.add_argument("--day", help="Day of month", type=int, required=True)
parser.add_argument(
    "--opdir", help="Directory for output files", default=None, type=str, required=False
)
parser.add_argument(
    "--type",
    help="actuals, anomalies, or differences",
    choices=["actuals", "anomalies", "differences"],
    type=str,
    required=True,
)
args = parser.parse_args()

opdir = None
if args.opdir is None:
    opdir = "%s/Proxy_Hadobs/webUI/HadUKGrid/daily/Tmax/%04d/%02d/%02d" % (
        os.getenv("SCRATCH"),
        args.year,
        args.month,
        args.day,
    )
else:
    opdir = args.opdir

if not os.path.isdir(opdir):
    os.makedirs(opdir)
fname = "%s/%s.html" % (opdir,args.type)
fh = open(fname, 'w')

def divMap(fh,pType):
    print('<div class="figure align-center" id="idM" style="width: 95%" >\n', file=fh)
    hType=pType
    if pType=='differences':
        hType='anomalies'
    print(('<a class="reference internal image-reference" '+
            'href="./HadUKGrid_map_%s.png"><img alt="HadUKGrid %s map" '+
            'src="./HadUKGrid_map_%s.png" style="width: 47%;" /></a>\n') %
            (hType,hType,hType), file=fh)
    print(('<a class="reference internal image-reference" '+
            'href="./UKPP_map_%s.png"><img alt="UKPP %s map" '+
            'src="./UKPP_map_%s.png" style="width: 47%;" /></a>\n') %
            (pType,pType,pType), file=fh)
    if pType=='differences':
        print(('<p class="caption"><span class="caption-text">'+
               'Left: HadUKGrid anomalies, '+
               'Right: UKPP differences from HadUKGrid, (both C).'+
               '</span></p>\n'), file=fh)
    else:
        print(('<p class="caption"><span class="caption-text">'+
               'Left: HadUKGrid %s, '+
               'Right: UKPP %s, (both C).'+
               '</span></p>\n') % (pType,pType),
                file=fh)
    print('</div>\n',file=fh)

def divTS(fh,pType):
    print('<div class="figure align-center" id="idTS" style="width: 95%" >\n', file=fh)
    print(('<a class="reference internal image-reference" '+
           'href="./TS_%s.png"><img alt="%s boxplot timeseries" '+
           'src="./TS_%s.png" style="width: 95%;" /></a>\n') % (pType,pType,pType),
           file=fh)
    if pType=='differences':
        print(('<p class="caption"><span class="caption-text">'+
               'Blue: HadUKGrid anomalies, '+
               'Right: UKPP differences from HadUKGrid, '+
               '(daily boxplots of all grid-point values (C)).'+
               '</span></p>\n'), file=fh)
    else:
        print(('<p class="caption"><span class="caption-text">'+
               'Blue: HadUKGrid %s, '+
               'Red: UKPP %s, '+
               '(daily boxplots of all grid-point values (C)).'+
               '</span></p>\n') % (pType,pType),
                file=fh)
    print('</div>\n',file=fh)

def divBody(fh,year,month,day,pType):
    print(('<div class="document">\n'+
           '<div class="documentwrapper">\n'+
           '<div class="bodywrapper">\n'+
           '<div class="body" role="main">\n'),file=fh)
    title = "Tmax %s for %04d-%02d-%02d" % (pType,year,month,day)
    print(('<div class="section" id="%s">\n'+
           '<h1>%s</h1>\n') % (title,title),file=fh)
    divTS(fh,pType)
    divMap(fh,pType)
    print('</div>\n</div>\n</div>\n</div>\n',file=fh)

def divDateNav(fh,year,month,day,pType):
    dte = datetime.date(year,month,day)
    dPrev =dte-datetime.timedelta(days=1)
    dNext = dte+datetime.timedelta(days=1)
    print(('<div class="related" role="navigation" aria-label="related navigation">\n'+
           '<h3>Navigation</h3>\n'+
           '<ul>\n'+
           '<li class="right" >\n'+
           '<a href="../../../%04d/%02d/%02d/%s.html" title="Next day"\n'+
           ' accesskey="N">Next day</a> |</li>\n'+
           '<li class="right" >\n'+
           '<a href="../../../%04d/%02d/%02d/%s.html" title="Previous day"\n'+
           ' accesskey="P">Previous day</a> |</li>\n'+
           '</ul>\n'+
           '</div>\n') % (dNext.year,dNext.month,dNext.day,pType,
                          dPrev.year,dPrev.month,dPrev.day,pType), file=fh)

def divSidebar(fh,pType):
    print(('<div class="sphinxsidebar" role="navigation" '+
               'aria-label="main navigation">\n'+
           '<div class="sphinxsidebarwrapper">\n'+
           '<h3>Change view</a></h3>\n'+
           '<ul class="current">\n'),file=fh)
           if pType=='actuals':
               print(('<li class="toctree-l1 current">'+
                      '<a class="current reference internal" href="#">'+
                      'Actuals</a></li>\n'),file=fh)
           else:
               print(('<li class="toctree-l1">'+
                      '<a class="reference internal" href="actuals.html">'+
                      'Actuals</a></li>\n'),file=fh)
           if pType=='anomalies':
               print(('<li class="toctree-l1 current">'+
                      '<a class="current reference internal" href="#">'+
                      'Anomalies</a></li>\n'),file=fh)
           else:
               print(('<li class="toctree-l1">'+
                      '<a class="reference internal" href="anomalies.html">'+
                      'Anomalies</a></li>\n'),file=fh)
           if pType=='differences':
               print(('<li class="toctree-l1 current">'+
                      '<a class="current reference internal" href="#">'+
                      'Differences</a></li>\n'),file=fh)
           else:
               print(('<li class="toctree-l1">'+
                      '<a class="reference internal" href="differences.html">'+
                      'Differences</a></li>\n'),file=fh)
          print(('</ul>\n'+
                 '<h3><a href="system documentation">System documentation</a></h3>\n'+
                 '<ul>\n'+
                 '<li><a href="https://github.com/philip-brohan/Proxy_Hadobs"'+
                 ' rel="nofollow">Github repository</a></li>\n'+
                 '</ul>\n'+
                 '<h3>Found a bug, or have a suggestion?</h3>\n'+ 
                 ' Please <a href="https://github.com/philip-brohan/'+
                 'Proxy_Hadobs/issues/new">raise an issue</a>.\n'+
                 '</div>\n'+
                 '</div>\n'),file=fh)

# Write the output
title = "Tmax %s for %04d-%02d-%02d" % (args.type,args.year,args.month,args.day)
print(('\n<!DOCTYPE html>\n'+
       '<html xmlns="http://www.w3.org/1999/xhtml">\n'+
       '<head>\n'+
       '<meta charset="utf-8" />\n'+
       '<title>%s</title>\n'+
       '<link rel="stylesheet" href="../../../../../../_static/sphinxdoc.css"'+
       '   type="text/css" />\n'+
       '<link rel="stylesheet" href="../../../../../../_static/pygments.css"'+
       '   type="text/css" />\n'+
       '</head><body>\n') % title, file=fh)
divDateNav(fh,args.year,args.month,args.day,args.type)
divSidebar(fh,args.type)
divBody(fh,args.year,args.month,args.day,args.type)
print('</body>\n</html>\n',file=fh)

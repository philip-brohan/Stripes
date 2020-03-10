#!/usr/bin/env python

# 20CRv3 stripes.
# Monthly, resolved in latitude, averaging in longitude, 
#  ssampling the ensemble.

import os
import iris
import numpy
import datetime
import pickle

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D

dts=[]
ndata=None
for year in range(1851,2016):
    sfile="%s/20CR/version_3/analyses/Stripes/TMP2m/%04d.pkl" % \
                                           (os.getenv('SCRATCH'),year)
    with open(sfile, "rb") as f:
       (ndyr,dtyr)  = pickle.load(f)

    dts.extend(dtyr)
    if ndata is None:
        ndata = ndyr
    else:
        ndata = numpy.ma.concatenate((ndata,ndyr))

pickle.dump( (ndata,dts), open( "20CRv3.pkl", "wb" ) )


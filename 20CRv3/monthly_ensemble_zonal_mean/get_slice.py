#!/usr/bin/env python

# 20CRv3 stripes.
# Monthly, resolved in latitude, averaging in longitude, 
#  sampling the ensemble.

# Get the sample for a specified year

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

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--year", help="Year",
                    type=int,required=True)
parser.add_argument("--opdir", help="Directory for output files",
                    default="%s/20CR/version_3/analyses/Stripes/TMP2m" % \
                                           os.getenv('SCRATCH'),
                    type=str,required=False)
args = parser.parse_args()
if not os.path.isdir(args.opdir):
    os.makedirs(args.opdir)

# Fix dask SPICE bug
import dask
dask.config.set(scheduler='single-threaded')

start=datetime.datetime(args.year,1,1,0,0)
end=datetime.datetime(args.year,12,31,23,59)

from get_sample import get_sample_cube

cpkl="%s/20CR/version_3/monthly_means/TMP2m.climatology.1961-90.pkl" % os.getenv('SCRATCH')
climatology=pickle.load(open(cpkl,'rb'))

rst = numpy.random.RandomState(seed=None)
dts=[]
ndata=None
for year in range(start.year,end.year+1,1):
    ey = min(year+1,end.year)
    (ndyr,dtyr) = get_sample_cube(datetime.datetime(year,1,1,0,0),
                                  datetime.datetime(year,12,31,23,59),
                                  climatology=climatology,
                                  new_grid=climatology[0],rstate=rst)
    dts.extend(dtyr)
    if ndata is None:
        ndata = ndyr
    else:
        ndata = numpy.ma.concatenate((ndata,ndyr))

cspf = "%s/%04d.pkl" % (args.opdir,args.year)
pickle.dump((ndata,dts),open(cspf,'wb'))
   

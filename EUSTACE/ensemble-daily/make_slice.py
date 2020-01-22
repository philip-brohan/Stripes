#!/usr/bin/env python

# Make an latitude slice from Eustace - at a given month,
#  sampling across day-of-month, longitude, and ensemble.


import os
import iris
import numpy
import pickle
import datetime

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--year", help="Year",
                    type=int,required=True)
parser.add_argument("--month", help="Month",
                    type=int,required=True)
parser.add_argument("--opdir", help="Directory for output files",
                    default="%s/EUSTACE/derived/ensemble-daily" % \
                                           os.getenv('SCRATCH'),
                    type=str,required=False)
args = parser.parse_args()
if not os.path.isdir(args.opdir):
    os.makedirs(args.opdir)

root_dir="%s/EUSTACE/1.0/" % os.getenv('SCRATCH')

# Fix dask SPICE bug
import dask
dask.config.set(scheduler='single-threaded')

# Array to store the sample in
ndata=numpy.ma.array(numpy.zeros((1,720)),mask=False)

# Load the ensemble for each day in the month (and anomalise)
h=[]
cdy = datetime.date(args.year,args.month,1)
while cdy.month==args.month:
    cldy=cdy.day
    if cdy.month==2 and cdy.day==29: cldy=28
    n=iris.load_cube("%s/climatology_1961_1990/%02d%02d.nc" % 
                      (root_dir,cdy.month,cldy),
                     iris.Constraint(cube_func=(lambda cell: cell.var_name == 'tas')))
    m=[]
    for member in range(10):
        e = iris.load_cube("%s/%04d/tas_global_eustace_0_%04d%02d%02d.nc" %
                          (root_dir,cdy.year,cdy.year,cdy.month,cdy.day),
                         iris.Constraint(cube_func=(lambda cell: cell.var_name == 'tasensemble_%d' % member)))
        e = e-n # to anomaly
        m.append(e)
    h.append(m)
    cdy += datetime.timedelta(days=1)

# Make the slice
for lat in range(720):
    day = numpy.random.randint(len(h))
    member = numpy.random.randint(10)
    rand_l = numpy.random.randint(0,1440)
    ndata[0,lat]=h[day][member].data[0,lat,rand_l]

# Store
dfile = "%s/%04d%02d.pkl" % (args.opdir,args.year,args.month)
pickle.dump( ndata, open( dfile, "wb" ) )

#!/usr/bin/env python

# Make an latitude slice from Eustace - at a given time,
#  sampling across longitude and ensemble.

# Actually, do this for every month in a year - makes a more
#  reasonable unit of work

import os
import iris
import numpy
import pickle

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--year", help="Year",
                    type=int,required=True)
parser.add_argument("--opdir", help="Directory for output files",
                    default="%s/EUSTACE/derived/ensemble-monthly_zonal_mean" % \
                                           os.getenv('SCRATCH'),
                    type=str,required=False)
args = parser.parse_args()
if not os.path.isdir(args.opdir):
    os.makedirs(args.opdir)

# Fix dask SPICE bug
import dask
dask.config.set(scheduler='single-threaded')

for month in range(1,13):

    # Load the Eustace monthly normals
    n=iris.load_cube("%s/EUSTACE/1.0/monthly/climatology_1961_1990/%02d.nc" % 
                      (os.getenv('SCRATCH'),month),
                     iris.Constraint(cube_func=(lambda cell: cell.var_name == 'tas')))

    # Array to store the sample in
    ndata=numpy.ma.array(numpy.zeros((1,720)),mask=False)

    # Load the ensemble (and anomalise)
    h=[]
    for member in range(10):
        e=iris.load_cube("%s/EUSTACE/1.0/monthly/%04d/%02d.nc" % 
                          (os.getenv('SCRATCH'),args.year,month),
                         iris.Constraint(cube_func=(lambda cell: cell.var_name == 'tasensemble_%d' % member)))
        e = e-n # to anomaly
        h.append(e)

    # Make the slice
    for lat in range(720):
        member = numpy.random.randint(10)
        ndata[0,lat]=numpy.mean(h[member].data[0,lat,:])
        rand_l = numpy.random.randint(0,1440)
        if numpy.ma.count_masked(h[member].data[0,lat,:]) > rand_l:
               ndata.mask[0,lat]=True

    # Store
    dfile = "%s/%04d%02d.pkl" % (args.opdir,args.year,month)
    pickle.dump( ndata, open( dfile, "wb" ) )

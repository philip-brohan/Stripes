#!/usr/bin/env python

# Make an latitude slice comparing Eustace and HadCRUT5 - for a given month,
#  mean across longitude, sampling across ensemble.

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
                    default="%s/EUSTACE/derived/HadCRUT5_comparison_zonal_mean" % \
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
    e=[]
    for member in range(10):
        m=iris.load_cube("%s/EUSTACE/1.0/monthly/%04d/%02d.nc" % 
                          (os.getenv('SCRATCH'),args.year,month),
                         iris.Constraint(cube_func=(lambda cell: \
                             cell.var_name == 'tasensemble_%d' % member)))
        m = m-n # to anomaly
        e.append(m)

    # Load the HadCRUT5 ensemble and regrid to match EUSTACE
    members = (1,2,3,4,5,56,57,58,59,60)
    h=[]
    for member in members:
       m = iris.load_cube("/scratch/hadcc/hadcrut5/build/HadCRUT5/analysis/"+
                     "HadCRUT.5.0.0.0.analysis.anomalies.%d.nc" % member,
                          iris.Constraint(time=lambda cell: \
                            cell.point.year==args.year and cell.point.month==month))
       m = m.regrid(e[0],iris.analysis.Nearest())
       h.append(m)

    # Make the slice
    for lat in range(720):
        m_e = numpy.random.randint(10)
        m_h = numpy.random.randint(10)
        rand_l = numpy.random.randint(0,1440)
        ndata[0,lat]=numpy.mean(h[m_h].data[lat,:]-e[m_e].data[0,lat,:])
        if numpy.ma.count_masked(h[m_h].data[lat,:]) > rand_l:
               ndata.mask[0,lat]=True
        if numpy.ma.count_masked(e[m_e].data[0,lat,:]) > rand_l:
               ndata.mask[0,lat]=True

    # Store
    dfile = "%s/%04d%02d.pkl" % (args.opdir,args.year,month)
    pickle.dump( ndata, open( dfile, "wb" ) )

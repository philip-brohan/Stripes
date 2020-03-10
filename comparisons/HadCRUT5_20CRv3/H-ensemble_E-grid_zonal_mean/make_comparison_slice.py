#!/usr/bin/env python

# Make an latitude slice comparing 20CRv3 and HadCRUT5 - for a given month,
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
                    default="%s/EUSTACE/derived/HadCRUT5_20CRv3_comparison_zonal_mean" % \
                                           os.getenv('SCRATCH'),
                    type=str,required=False)
args = parser.parse_args()
if not os.path.isdir(args.opdir):
    os.makedirs(args.opdir)

# Fix dask SPICE bug
import dask
dask.config.set(scheduler='single-threaded')

# Get EUSTACE field for grid dimensions
egrid = iris.load_cube(("%s/EUSTACE/1.0/1969/"+
                        "tas_global_eustace_0_19690312.nc") % 
                        os.getenv('SCRATCH'),
            iris.Constraint(cube_func=(lambda c: c.var_name == 'tas')))

# Make the 20CR climatology
cpkl="%s/20CR/version_3/monthly_means/TMP2m.climatology.1961-90.pkl" % os.getenv('SCRATCH')
climatology=pickle.load(open(cpkl,'rb'))

for month in range(1,13):

    # Array to store the sample in
    ndata=numpy.ma.array(numpy.zeros((1,720)),mask=False)

    # Load the 20CR data, anomalise, and regrid to EUSTACE grid
    e=[]
    for member in range(1,81):
        h=iris.load_cube('%s/20CR/version_3/monthly_means/%04d/TMP2m.%04d.mnmean_mem%03d.nc' % 
                                                           (os.getenv('SCRATCH'),args.year,args.year,member),
                         iris.Constraint(name='air_temperature') &
                         iris.Constraint(time=lambda cell: \
                            cell.point.year==args.year and cell.point.month==month))
        h=h.collapsed('height', iris.analysis.MEAN)
        h.remove_coord('height')

        # Anomalise
        h.data -= climatology[month-1].data

        h = h.regrid(egrid,iris.analysis.Nearest())
        e.append(h)

    # Load the HadCRUT5 ensemble and regrid to EUSTACE grid
    members = (1,2,3,4,5,56,57,58,59,60)
    h=[]
    for member in members:
       m = iris.load_cube("/scratch/hadcc/hadcrut5/build/HadCRUT5/analysis/"+
                     "HadCRUT.5.0.0.0.analysis.anomalies.%d.nc" % member,
                          iris.Constraint(time=lambda cell: \
                            cell.point.year==args.year and cell.point.month==month))
       m = m.regrid(egrid,iris.analysis.Nearest())
       h.append(m)

    # Make the slice
    for lat in range(720):
        m_h = numpy.random.randint(10)
        m_t = numpy.random.randint(80)
        rand_l = numpy.random.randint(0,1440)
        ndata[0,lat]=numpy.mean(h[m_h].data[lat,:]-e[m_t].data[lat,:])
        if numpy.ma.count_masked(h[m_h].data[lat,:]) > rand_l:
               ndata.mask[0,lat]=True

    # Store
    dfile = "%s/%04d%02d.pkl" % (args.opdir,args.year,month)
    pickle.dump( ndata, open( dfile, "wb" ) )

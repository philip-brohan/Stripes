#!/usr/bin/env python

# Make an latitude slice comparing 20CRv3 and ERA5 - for a given month,
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
                    default="%s/EUSTACE/derived/ERA5_20CRv3_comparison" % \
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
n=[]
for m in range(1,13):
    mc=iris.Constraint(time=lambda cell: cell.point.month == m and \
                                         cell.point.year > 1980 and \
                                         cell.point.year < 2011)
    h=iris.load_cube('%s/20CR/version_3/monthly_means/air.2m.mon.mean.nc' % 
                                                   os.getenv('SCRATCH'),
                 iris.Constraint(name='air_temperature') & mc)
    n.append(h.extract(mc).collapsed('time', iris.analysis.MEAN))

# Make the ERA5 climatology
n5=[]
for m in range(1,13):
    mc=iris.Constraint(time=lambda cell: cell.point.month == m and \
                                         cell.point.year > (1981-1) and \
                                         cell.point.year < (2010+1))
    h=iris.load('%s/ERA5/monthly_averaged_ensemble_members/t2m.nc' % 
                                                   os.getenv('SCRATCH'),
                 iris.Constraint(name='2 metre temperature') & mc)
    # ERA5 data bug - get a masked copy along with the data
    #   pick the real version.
    if numpy.ma.is_masked(h[0].data):
        h = h[1]
    else:
        h = h[0]
    n5.append(h.extract(mc).collapsed(['time','ensemble_member'],
                                     iris.analysis.MEAN))

for month in range(1,13):

    # Array to store the sample in
    ndata=numpy.ma.array(numpy.zeros((1,720)),mask=False)

    # Load the 20CR data, anomalise, and regrid to EUSTACE grid
    mc=iris.Constraint(time=lambda cell: cell.point.month == month and \
                                         cell.point.year == args.year)
    e=iris.load_cube('%s/20CR/version_3/monthly_means/air.2m.mon.mean.nc' % 
                                                   os.getenv('SCRATCH'),
                 iris.Constraint(name='air_temperature') & mc)
    e = e - n[month-1]
    e = e.regrid(egrid,iris.analysis.Nearest())

    # Load the ERA5 data
    h=[]
    for member in range(10):
        m = iris.load('%s/ERA5/monthly_averaged_ensemble_members/t2m.nc' %
                                                           os.getenv('SCRATCH'),
                          iris.Constraint(ensemble_member=member) & mc)
        if numpy.ma.is_masked(m[0].data):
            m = m[1]
        else:
            m = m[0]

        m = m - n5[month-1]

        m = m.regrid(egrid,iris.analysis.Nearest())
        h.append(m)

    # Make the slice
    for lat in range(720):
        m_h = numpy.random.randint(10)
        rand_l = numpy.random.randint(0,1440)
        ndata[0,lat]=h[m_h].data[lat,rand_l]-e.data[lat,rand_l]

    # Store
    dfile = "%s/%04d%02d.pkl" % (args.opdir,args.year,month)
    pickle.dump( ndata, open( dfile, "wb" ) )
    print("Wibble %04d %02d" % (args.year,month))
    print("Wibble %f" % numpy.mean(ndata))


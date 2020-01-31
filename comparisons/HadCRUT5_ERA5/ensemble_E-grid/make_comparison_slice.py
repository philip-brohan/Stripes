#!/usr/bin/env python

# Make an latitude slice comparing ERA5 and HadCRUT5 - for a given month,
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
                    default="%s/EUSTACE/derived/HadCRUT5_ERA5_comparison" % \
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

# Make the ERA5 climatology
n5=[]
for mo in range(1,13):
    mc=iris.Constraint(time=lambda cell: cell.point.month == mo and \
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

# load the HadCRUT5 climatology adjustment (to 1981-2010 from 1961-90)
with open(("%s/EUSTACE/derived/HadCRUT5_ERA5_comparison/"+
           "HadCRUT5_climatology_adjustment.pkl") % os.getenv('SCRATCH'),
           'rb') as fp:
    n= pickle.load(fp)

for month in range(1,13):

    # Array to store the sample in
    ndata=numpy.ma.array(numpy.zeros((1,720)),mask=False)

    # Load the ERA5 data, anomalise, and regrid to EUSTACE grid
    e=[]
    for member in range(10):
        m = iris.load('%s/ERA5/monthly_averaged_ensemble_members/t2m.nc' %
                                                           os.getenv('SCRATCH'),
                          iris.Constraint(ensemble_member=member) & 
                          iris.Constraint(time=lambda cell: \
                            cell.point.year==args.year and cell.point.month==month))
        if numpy.ma.is_masked(m[0].data):
            m = m[1]
        else:
            m = m[0]

        m = m - n5[month-1]

        m = m.regrid(egrid,iris.analysis.Nearest())
        e.append(m)

    # Load the HadCRUT5 ensemble, adjust, and regrid to EUSTACE grid
    members = (1,2,3,4,5,56,57,58,59,60)
    h=[]
    for member in members:
       m = iris.load_cube("/scratch/hadcc/hadcrut5/build/HadCRUT5/analysis/"+
                     "HadCRUT.5.0.0.0.analysis.anomalies.%d.nc" % member,
                          iris.Constraint(time=lambda cell: \
                            cell.point.year==args.year and cell.point.month==month))
       m = m - n[month-1]
       m = m.regrid(egrid,iris.analysis.Nearest())
       h.append(m)

    # Make the slice
    for lat in range(720):
        m_h = numpy.random.randint(10)
        m_e = numpy.random.randint(10)
        rand_l = numpy.random.randint(0,1440)
        ndata[0,lat]=h[m_h].data[lat,rand_l]-e[m_e].data[lat,rand_l]

    # Store
    dfile = "%s/%04d%02d.pkl" % (args.opdir,args.year,month)
    pickle.dump( ndata, open( dfile, "wb" ) )

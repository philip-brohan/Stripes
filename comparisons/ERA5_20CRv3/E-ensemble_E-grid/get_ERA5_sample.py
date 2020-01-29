#!/usr/bin/env python

# Get a climate-stripes sample from ERA5
# Monthly, resolved in latitude, sampling in longitude, 
#   mean across the ensemble.

import os
import sys
import iris
import numpy
import datetime
import pickle

start=datetime.datetime(1851,1,1,0,0)
end=datetime.datetime(2018,12,31,23,59)

sys.path.append('%s/../../../ERA5/ensemble/' % 
                                  os.path.dirname(__file__))
from get_sample import get_sample_cube

egrid = iris.load_cube(("%s/EUSTACE/1.0/1969/"+
                        "tas_global_eustace_0_19690312.nc") % 
                        os.getenv('SCRATCH'),
            iris.Constraint(cube_func=(lambda c: c.var_name == 'tas')))

# Make the climatology
n=[]
for m in range(1,13):
    mc=iris.Constraint(time=lambda cell: cell.point.month == m and \
                                         cell.point.year > (1981-1) and \
                                         cell.point.year < (2010+1))
    h=iris.load('%s/ERA5/monthly_averaged_ensemble_members/t2m.nc' % 
                                                   os.getenv('SCRATCH'),
                 iris.Constraint(name='2 metre temperature') & mc)[1]
    n.append(h.extract(mc).collapsed(['time','ensemble_member'],
                                     iris.analysis.MEAN))

# Process in batches or we'll run out of memory.
rst = numpy.random.RandomState(seed=0)
dts=[]
ndata=None
for year in range(1979,end.year+1,5):
    ey = min(year+5,end.year)
    (ndyr,dtyr) = get_sample_cube(datetime.datetime(year,1,1,0,0),
                                  datetime.datetime(ey,12,31,23,59),
                                  climatology=n,
                                  new_grid=egrid,rstate=rst)
    dts.extend(dtyr)
    if ndata is None:
        ndata = ndyr
    else:
        ndata = numpy.ma.concatenate((ndata,ndyr))

pickle.dump( (ndata,dts), open( "ERA5.pkl", "wb" ) )

#!/usr/bin/env python

# Get a climate-stripes sample from HadCRUT5
# Monthly, resolved in latitude, sampling in longitude, sampling the ensemble.
# Regridded to the EUSTACE grid.

import os
import sys
import iris
import numpy
import datetime
import pickle

start=datetime.datetime(1851,1,1,0,0)
end=datetime.datetime(2018,12,31,23,59)

sys.path.append('%s/../../../HadCRUT5/ensemble/' % os.path.dirname(__file__))
from get_sample import get_sample_cube

egrid = iris.load_cube(("%s/EUSTACE/1.0/1969/"+
                        "tas_global_eustace_0_19690312.nc") % 
                        os.getenv('SCRATCH'),
            iris.Constraint(cube_func=(lambda c: c.var_name == 'tas')))

# Process in batches or we'll run out of memory.
rst = numpy.random.RandomState(seed=0)
dts=[]
ndata=None
for year in range(start.year,end.year+1,10):
    print("\n\n%4d\n\n" % year)
    ey = min(year+10,end.year)
    (ndyr,dtyr) = get_sample_cube(datetime.datetime(year,1,1,0,0),
                                  datetime.datetime(ey,12,31,23,59),
                                  new_grid=egrid,rstate=rst)
    dts.extend(dtyr)
    if ndata is None:
        ndata = ndyr
    else:
        ndata = numpy.ma.concatenate((ndata,ndyr))

pickle.dump( (ndata,dts), open( "HadCRUT5.pkl", "wb" ) )

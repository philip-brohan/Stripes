# Get the sample cube for HadCRUT5
# Monthly, resolved in longitude, sampling in latitude, sampling the ensemble.

import os
import iris
import numpy
import datetime

def get_sample_cube(start=datetime.datetime(1851,1,1,0,0),
                    end=datetime.datetime(2018,12,31,23,59),
                    new_grid=None,rstate=None):

    # Choose ten ensemble members (Should be half odd and half even,
    #   and half from 1-50, half from 51-100)
    members = (1,2,3,4,5,56,57,58,59,60)

    # Might want the latitude random sampling to be reproducible
    if rstate is None:
        r_lat = numpy.random.RandomState(seed=None)
    else:
        r_lat = rstate
    # The ensemble random sampling need not be reproducible
    r_ensemble = numpy.random.RandomState(seed=None)

    # Load the HadCRUT5 analysis data
    h=[]
    for member in members:
       m = iris.load_cube("/scratch/hadcc/hadcrut5/build/HadCRUT5/analysis/"+
                     "HadCRUT.5.0.0.0.analysis.anomalies.%d.nc" % member,
                     iris.Constraint(time=lambda cell: start <= cell.point <=end))
       if new_grid is not None:
           m = m.regrid(new_grid,iris.analysis.Nearest())
       h.append(m)

    dts = h[0].coords('time')[0].units.num2date(h[0].coords('time')[0].points)

    # Pick a random latitude at each month
    s=h[0].data.shape
    ndata=numpy.ma.array(numpy.zeros((s[0],s[2])),mask=True)
    for t in range(s[0]):
       for lon in range(s[2]):
           member = r_ensemble.randint(len(members))
           rand_l = r_lat.randint(0,s[1])
           ndata[t,lon]=h[member].data[t,rand_l,lon]

    return (ndata,dts)


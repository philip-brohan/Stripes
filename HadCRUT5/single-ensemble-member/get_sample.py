# Get the sample cube for HadCRUT5
# Monthly, resolved in latitude, sampling in longitude, one ensemble member.

import os
import iris
import numpy
import datetime

def get_sample_cube(start=datetime.datetime(1851,1,1,0,0),
                    end=datetime.datetime(2018,12,31,23,59),
                    new_grid=None,rstate=None):

    # Might want the longitude random sampling to be reproducible
    if rstate is None:
        r_long = numpy.random.RandomState(seed=None)
    else:
        r_long = rstate
    # The ensemble random sampling need not be reproducible
    r_ensemble = numpy.random.RandomState(seed=None)

    # Choose one ensemble member (arbitrarily)
    member = r_ensemble.randint(100)+1

    # Load the HadCRUT5 analysis data
    h=iris.load_cube("/scratch/hadcc/hadcrut5/build/HadCRUT5/analysis/"+
                     "HadCRUT.5.0.0.0.analysis.anomalies.%d.nc" % member,
                     iris.Constraint(time=lambda cell: start <= cell.point <=end))
    if new_grid is not None:
        h = h.regrid(new_grid,iris.analysis.Nearest())

    dts = h.coords('time')[0].units.num2date(h.coords('time')[0].points)

    # Sample in Longitude
    s=h.data.shape
    ndata = numpy.zeros((s[0],s[1]))
    for t in range(s[0]):
        for lat in range(s[1]):
            rand_l = numpy.random.randint(0,s[2])
            ndata[t,lat]=h.data[t,lat,rand_l]

    return (ndata,dts)


# Get the sample cube for HadCRUT5
# Monthly, resolved in latitude, sampling in longitude, one ensemble member.

import os
import iris
import numpy
import datetime

def get_sample_cube(start=datetime.datetime(1851,1,1,0,0),
                    end=datetime.datetime(2018,12,31,23,59)):

    # Choose one ensemble member (arbitrarily)
    member = numpy.random.randint(100)+1

    # Load the HadCRUT5 analysis data
    h=iris.load_cube("/scratch/hadcc/hadcrut5/build/HadCRUT5/analysis/"+
                     "HadCRUT.5.0.0.0.analysis.anomalies.%d.nc" % member,
                     iris.Constraint(time=lambda cell: start <= cell.point <=end))

    dts = h.coords('time')[0].units.num2date(h.coords('time')[0].points)

    # Sample in Longitude
    p=h.extract(iris.Constraint(longitude=0))
    s=h.data.shape
    for t in range(s[0]):
        for lat in range(s[1]):
            rand_l = numpy.random.randint(0,s[2])
            p.data[t,lat]=h.data[t,lat,rand_l]
    h=p
    ndata=h.data
    return (ndata,dts)


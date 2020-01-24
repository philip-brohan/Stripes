# Get the sample cube for 20CR

import os
import iris
import numpy
import datetime

def get_sample_cube(start=datetime.datetime(1851,1,1,0,0),
                    end=datetime.datetime(2018,12,31,23,59),
                    climstart=1961,climend=1990):

    # Load the model data
    h=iris.load_cube('%s/20CR/version_3/monthly_means/air.2m.mon.mean.nc' % 
                                                       os.getenv('SCRATCH'),
                     iris.Constraint(name='air_temperature') &
                     iris.Constraint(time=lambda cell: \
                                     start <= cell.point <=end))
    dts = h.coords('time')[0].units.num2date(h.coords('time')[0].points)

    # Make the climatology
    n=[]
    for m in range(1,13):
        mc=iris.Constraint(time=lambda cell: cell.point.month == m and \
                                             cell.point.year > (climstart-1) and \
                                             cell.point.year < (climend+1))
        n.append(h.extract(mc).collapsed('time', iris.analysis.MEAN))

    # Anomalise
    for tidx in range(len(dts)):
        midx=dts[tidx].month-1
        h.data[tidx,:,:] -= n[midx].data

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


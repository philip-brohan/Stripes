# Get the sample cube for 20CR

import os
import iris
import numpy
import datetime

def get_sample_cube(start=datetime.datetime(1851,1,1,0,0),
                    end=datetime.datetime(2018,12,31,23,59),
                    climatology=None,
                    climstart=1961,climend=1991,
                    new_grid=None,rstate=None):

    # Might want the latitude random sampling to be reproducible
    if rstate is None:
        r_lat = numpy.random.RandomState(seed=None)
    else:
        r_lat = rstate

    # Make the climatology, if not supplied
    if climatology is None:
        climatology=[]
        for m in range(1,13):
            mc=iris.Constraint(time=lambda cell: cell.point.month == m and \
                                                 cell.point.year > (climstart-1) and \
                                                 cell.point.year < (climend+1))
            h=iris.load_cube('%s/20CR/version_3/monthly_means/air.2m.mon.mean.nc' % 
                                                           os.getenv('SCRATCH'),
                         iris.Constraint(name='air_temperature') & mc)
            climatology.append(h.extract(mc).collapsed('time', iris.analysis.MEAN))

    # Load the model data
    h=iris.load_cube('%s/20CR/version_3/monthly_means/air.2m.mon.mean.nc' % 
                                                       os.getenv('SCRATCH'),
                     iris.Constraint(name='air_temperature') &
                     iris.Constraint(time=lambda cell: \
                                     start <= cell.point <=end))

    dts = h.coords('time')[0].units.num2date(h.coords('time')[0].points)

    # Anomalise
    for tidx in range(len(dts)):
        midx=dts[tidx].month-1
        h.data[tidx,:,:] -= climatology[midx].data

    if new_grid is not None:
        h = h.regrid(new_grid,iris.analysis.Nearest())

    # Sample in Latitude
    s=h.data.shape
    ndata=numpy.ma.array(numpy.zeros((s[0],s[2])),mask=True)
    for t in range(s[0]):
        for lon in range(s[2]):
            rand_l = r_lat.randint(0,s[1])
            ndata[t,lon]=h.data[t,rand_l,lon]
    return (ndata,dts)


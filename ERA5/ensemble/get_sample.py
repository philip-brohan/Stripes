# Get the sample cube for ERA5
# Monthly, resolved in latitude, sampling in longitude, sampling the ensemble.

import os
import iris
import numpy
import datetime

def get_sample_cube(start=datetime.datetime(1851,1,1,0,0),
                    end=datetime.datetime(2018,12,31,23,59),
                    climatology=None,
                    climstart=1981,climend=2010,
                    new_grid=None,rstate=None):

    # Might want the longitude random sampling to be reproducible
    if rstate is None:
        r_long = numpy.random.RandomState(seed=None)
    else:
        r_long = rstate
    # The ensemble random sampling need not be reproducible
    r_ensemble = numpy.random.RandomState(seed=None)

    # Make the climatology, if not supplied
    if climatology is None:
        climatology=[]
        for m in range(1,13):
            mc=iris.Constraint(time=lambda cell: cell.point.month == m and \
                                                 cell.point.year > (climstart-1) and \
                                                 cell.point.year < (climend+1))
            h=iris.load('%s/ERA5/monthly_averaged_ensemble_members/t2m.nc' % 
                                                           os.getenv('SCRATCH'),
                         iris.Constraint(name='2 metre temperature') & mc)
            # ERA5 data bug - get a masked copy along with the data
            #   pick the real version.
            if numpy.ma.is_masked(h[0].data):
                h = h[1]
            else:
                h = h[0]
            climatology.append(h.extract(mc).collapsed(['time','ensemble_member'],
                                                                       iris.analysis.MEAN))

    # Load the ERA5 data
    h=[]
    for member in range(10):
        m = iris.load('%s/ERA5/monthly_averaged_ensemble_members/t2m.nc' %
                                                           os.getenv('SCRATCH'),
                          iris.Constraint(ensemble_member=member) & \
                          iris.Constraint(time=lambda cell: start <= cell.point <=end))
        if numpy.ma.is_masked(m[0].data):
            m = m[1]
        else:
            m = m[0]

        dts = m.coords('time')[0].units.num2date(m.coords('time')[0].points)

        # Anomalise
        for tidx in range(len(dts)):
            midx=dts[tidx].month-1
            m.data[tidx,:,:] -= climatology[midx].data

        if new_grid is not None:
            m = m.regrid(new_grid,iris.analysis.Nearest())
        h.append(m)

    dts = h[0].coords('time')[0].units.num2date(h[0].coords('time')[0].points)

    # Pick a random longitude at each month
    s=h[0].data.shape
    ndata=numpy.ma.array(numpy.zeros((s[0],s[1])),mask=True)
    for t in range(s[0]):
       for lat in range(s[1]):
           member = r_ensemble.randint(len(h))
           rand_l = r_long.randint(0,s[2])
           ndata[t,lat]=h[member].data[t,lat,rand_l]

    return (ndata,dts)


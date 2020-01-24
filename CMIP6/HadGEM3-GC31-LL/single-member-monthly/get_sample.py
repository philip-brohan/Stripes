# Get the sample cube for HadGEM3-GC31-LL

import os
import iris
import numpy
import datetime
import cftime
import glob

def get_sample_cube(start=cftime._cftime.Datetime360Day(1851,1,1),
                    end=cftime._cftime.Datetime360Day(2018,12,30),
                    climstart=1961,climend=1990):

    # Load the model data
    ifiles= glob.glob(("%s/CMIP6/HadGEM3-GC31-LL/Historical/"+
                       "tas_Amon_*r1i1p1f3_*.nc") % os.getenv('SCRATCH'))
    a=[]
    for ifile in ifiles:
        c=iris.load_cube(ifile,
                         iris.Constraint(name='air_temperature') &
                         iris.Constraint(time=lambda cell: start <= cell.point <=end))
        a.append(c)
        a[-1].attributes=a[0].attributes  # otherwise won't concatenate

    h=iris.cube.CubeList(a).concatenate_cube()
    dts = h.coords('time')[0].units.num2date(h.coords('time')[0].points)

    # Make the climatology
    n=[]
    for m in range(1,13):
        mc=iris.Constraint(time=lambda cell: cell.point.month == m and \
                                             cell.point.year > (climstart-1) and\
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


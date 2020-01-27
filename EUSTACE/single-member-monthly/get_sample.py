# Get the sample cube for EUSTACE
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

    # Choose one ensemble member (arbitrarily)
    member = numpy.random.randint(10)

    # Load the Eustace monthly normals
    n=[]
    for month in range(1,13):
        h=iris.load_cube("%s/EUSTACE/1.0/monthly/climatology_1961_1990/%02d.nc" % 
                          (os.getenv('SCRATCH'),month),
                         iris.Constraint(cube_func=(lambda cell: cell.var_name == 'tas')))
        n.append(h)
    
    # Array to store the sample in
    mlen=(end.year-start.year)*12+(end.month-start.month+1)
    llen=720
    if new_grid is not None: 
        llen = len(new_grid.coords('latitude')[0].points)
    ndata=numpy.ma.array(numpy.zeros((mlen,llen)),mask=True)
    dts=[]
    # Assemble the sample slice by slice
    t=0
    for year in range(start.year,end.year+1):
        for month in range(1,13):
            if ( (year==start.year and month<start.month) or
                 (year==end.year and month>end.month) ): continue
            try:
                h=iris.load_cube("%s/EUSTACE/1.0/monthly/%04d/%02d.nc" % 
                                  (os.getenv('SCRATCH'),year,month),
                                 iris.Constraint(cube_func=(lambda cell:\
                                   cell.var_name == 'tasensemble_%d' % member)))
            except Exception:
                t += 1
                dts.append(datetime.datetime(year,month,15))
                continue  # No data
    
            h = h-n[month-1] # to anomaly
            if new_grid is not None:
                h = h.regrid(new_grid,iris.analysis.Nearest())

            for lat in range(llen):
                rand_l = numpy.random.randint(0,h.data.shape[2])
                ndata[t,lat]=h.data[0,lat,rand_l]
            t += 1
            dts.append(datetime.datetime(year,month,15))
    
    return (ndata,dts)


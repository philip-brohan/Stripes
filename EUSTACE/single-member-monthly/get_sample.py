# Get the sample cube for EUSTACE
# Monthly, resolved in latitude, sampling in longitude, one ensemble member.

import os
import iris
import numpy
import datetime

def get_sample_cube(start=datetime.datetime(1851,1,1,0,0),
                    end=datetime.datetime(2018,12,31,23,59)):

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
    ndata=numpy.ma.array(numpy.zeros(((2016-1850)*12,720)),mask=False)
    dts=[]
    # Assemble the sample slice by slice
    for year in range(1850,2016):
        for month in range(1,13):
            t=(year-1850)*12+month-1
            h=iris.load_cube("%s/EUSTACE/1.0/monthly/%04d/%02d.nc" % 
                              (os.getenv('SCRATCH'),year,month),
                             iris.Constraint(cube_func=(lambda cell:\
                               cell.var_name == 'tasensemble_%d' % member)))
            h = h-n[month-1] # to anomaly
            for lat in range(720):
                rand_l = numpy.random.randint(0,1440)
                ndata[t,lat]=h.data[0,lat,rand_l]
            dts.append(datetime.datetime(year,month,15))
    
    return (ndata,dts)


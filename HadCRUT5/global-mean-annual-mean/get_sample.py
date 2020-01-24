# Get the sample cube for HadCRUT5
# Basic version, global-mean-annual-mean, one ensemble member.

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

    # Make annual averages
    iris.coord_categorisation.add_year(h,'time',name='year')
    h=h.aggregated_by('year',iris.analysis.MEAN)
    # Make area-weighted global means
    grid_areas = iris.analysis.cartography.area_weights(h)
    h_mean = h.collapsed(['latitude', 'longitude'],
                               iris.analysis.MEAN,
                               weights=grid_areas)
    
    ndata=h_mean.data
    dts = h_mean.coords('time')[0].units.num2date(h_mean.coords('time')[0].points)
    return (ndata,dts)


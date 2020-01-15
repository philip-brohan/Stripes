#!/usr/bin/env python

# Make a climate-stripes image from HadCRUT5
# Basic version, global-mean-annual-mean, one ensemble member.

import os
import iris
import iris.coord_categorisation
import numpy
import datetime

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

start=datetime.datetime(1851,1,1,0,0)
end=datetime.datetime(2018,12,31,23,59)

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
dts = h.coords('time')[0].units.num2date(h.coords('time')[0].points)
ndata=h_mean.data

# Plot the resulting array as a 2d colourmap
fig=Figure(figsize=(19.2,6),              # Width, Height (inches)
           dpi=100,
           facecolor=(0.5,0.5,0.5,1),
           edgecolor=None,
           linewidth=0.0,
           frameon=False,                
           subplotpars=None,
           tight_layout=None)
canvas=FigureCanvas(fig)
matplotlib.rc('image',aspect='auto')

# Add a textured grey background
s=(2000,100)
ax2 = fig.add_axes([0,0,1,1],facecolor='green')
ax2.set_axis_off() # Don't want surrounding x and y axis
nd2=numpy.random.rand(s[1],s[0])
clrs=[]
for shade in numpy.linspace(.42+.01,.36+.01):
    clrs.append((shade,shade,shade,1))
y = numpy.linspace(0,1,s[1])
x = numpy.linspace(0,1,s[0])
img = ax2.pcolormesh(x,y,nd2,
                        cmap=matplotlib.colors.ListedColormap(clrs),
                        alpha=1.0,
                        shading='gouraud',
                        zorder=10)

# Plot the stripes
ax = fig.add_axes([0,0,1,1],facecolor='black',
                  xlim=((start+datetime.timedelta(days=183)).timestamp(),
                        (end-datetime.timedelta(days=183)).timestamp()),
                  ylim=(0,1))
ax.set_axis_off() 

nd2=numpy.reshape(ndata,(ndata.shape[0],1))
nd3=numpy.concatenate((nd2,nd2),1)
nd3 = numpy.transpose(nd3)
y = (0,1)
x = [a.timestamp() for a in dts]
img = ax.pcolorfast(x,y,numpy.cbrt(nd3),
                        cmap='RdYlBu_r',
                        alpha=1.0,
                        vmin=-1.0,
                        vmax=1.0,
                        zorder=100)

fig.savefig('basic.png')

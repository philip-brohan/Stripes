#!/usr/bin/env python

# 20CRv3 stripes.
# Monthly, resolved in latitude, sampling in longitude, ensemble mean.

import os
import iris
import numpy
import datetime

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

start=datetime.datetime(1851,1,1,0,0)
end=datetime.datetime(2018,12,31,23,59)

# Load the 20CR data
h=iris.load_cube('%s/20CR/version_3/monthly_means/air.2m.mon.mean.nc' % os.getenv('SCRATCH'),
                 iris.Constraint(name='air_temperature') &
                 iris.Constraint(time=lambda cell: start <= cell.point <=end))
dts = h.coords('time')[0].units.num2date(h.coords('time')[0].points)

# Get the climatology
n=[]
for m in range(1,13):
    mc=iris.Constraint(time=lambda cell: cell.point.month == m and cell.point.year>1960 and cell.point.year<1991)
    n.append(h.extract(mc).collapsed('time', iris.analysis.MEAN))

# Anomalise
for tidx in range(len(h.coord('time').points)):
    tpt=datetime.datetime(1800,1,1)+datetime.timedelta(hours=h.coord('time').points[tidx])
    midx=tpt.month-1
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
ax2.set_axis_off() 
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
                  xlim=((start+datetime.timedelta(days=1)).timestamp(),
                        (end-datetime.timedelta(days=1)).timestamp()),
                  ylim=(0,1))
ax.set_axis_off()

ndata=numpy.transpose(ndata)
s=ndata.shape
y = numpy.linspace(0,1,s[0]+1)
x = [(a-datetime.timedelta(days=15)).timestamp() for a in dts]
x.append((dts[-1]+datetime.timedelta(days=15)).timestamp())
img = ax.pcolorfast(x,y,numpy.cbrt(ndata),
                        cmap='RdYlBu_r',
                        alpha=1.0,
                        vmin=-1.7,
                        vmax=1.7,
                        zorder=100)

fig.savefig('20CRv3.png')


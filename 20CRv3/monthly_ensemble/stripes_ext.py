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
from matplotlib.lines import Line2D

start=datetime.datetime(1806,1,1,0,0)
end=datetime.datetime(2015,12,31,23,59)

from get_sample import get_sample_cube

climatology=[]
e=[]
for year in range(1961,1990):
     h = None
     for member in range(1,2):
         f=iris.load_cube('%s/20CR/version_3/monthly_means/%04d/TMP2m.%04d.mnmean_mem%03d.nc' % 
                                                           (os.getenv('SCRATCH'),year,year,member),
                         iris.Constraint(name='air_temperature'))
         f=f.collapsed('height', iris.analysis.MEAN)
         #f.remove_coord('height')
         if h is None:
             h=f
         else:
             h.data += f.data
     h.data /= 1
     h.attributes=None
     e.append(h)

e=iris.cube.CubeList(e).concatenate_cube()

for month in range(1,13):
     m=e.extract(iris.Constraint(time=lambda cell: cell.point.month == month))
     climatology.append(m.collapsed('time', iris.analysis.MEAN))

# Process in batches or we'll run out of memory.
rst = numpy.random.RandomState(seed=None)
dts=[]
ndata=None
for year in range(start.year,end.year+1,1):
    ey = min(year+1,end.year)
    (ndyr,dtyr) = get_sample_cube(datetime.datetime(year,1,1,0,0),
                                  datetime.datetime(year,12,31,23,59),
                                  climatology=climatology,
                                  new_grid=climatology[0],rstate=rst)
    dts.extend(dtyr)
    if ndata is None:
        ndata = ndyr
    else:
        ndata = numpy.ma.concatenate((ndata,ndyr))

# Plot the resulting array as a 2d colourmap
fig=Figure(figsize=(19.2,6),              # Width, Height (inches)
           dpi=300,
           facecolor=(0.5,0.5,0.5,1),
           edgecolor=None,
           linewidth=0.0,
           frameon=False,                
           subplotpars=None,
           tight_layout=None)
canvas=FigureCanvas(fig)
matplotlib.rc('image',aspect='auto')

def add_latline(ax,latitude):
    latl = (latitude+90)/180
    ax.add_line(Line2D([start.timestamp(),end.timestamp()], 
                       [latl,latl], 
                       linewidth=0.5, 
                       color=(0.8,0.8,0.8,1),
                       zorder=200))

# Add a textured grey background
s=(2000,600)
ax2 = fig.add_axes([0,0.05,1,0.95],facecolor='green')
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
ax = fig.add_axes([0,0.05,1,0.95],facecolor='black',
                  xlim=((start+datetime.timedelta(days=1)).timestamp(),
                        (end-datetime.timedelta(days=1)).timestamp()),
                  ylim=(1,0))
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

# Add a date grid
axg = fig.add_axes([0,0,1,1],facecolor='green',
                  xlim=((start+datetime.timedelta(days=1)).timestamp(),
                        (end-datetime.timedelta(days=1)).timestamp()),
                  ylim=(0,1))
axg.set_axis_off()
def add_dateline(ax,year):
    x = datetime.datetime(year,1,1,0,0).timestamp()
    ax.add_line(Line2D([x,x], [0.04,1.0], 
                linewidth=0.5, 
                color=(0.8,0.8,0.8,1),
                       zorder=200))
    ax.text(x,0.025,
         "%04d" % year,
         horizontalalignment='center',
         verticalalignment='center',
         color='black',
         size=14,
         clip_on=True,
         zorder=200)
    
for year in range(1810,2020,10):
    add_dateline(axg,year)

fig.savefig('20CRv3_ext.png')


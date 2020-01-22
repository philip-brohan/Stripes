#!/usr/bin/env python

# Make an extended climate-stripes image from Eustace
# Samplid day in month, resolved in latitude, sampling in longitude, 
#   sampling across the ensemble.

# Delegates making the slices to the parallelisable make_slice script.
# This script only does the plotting.

import os
import numpy
import datetime
import pickle

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

start=datetime.datetime(1851,1,1,0,0)
end=datetime.datetime(2018,12,31,23,59)

slice_dir = "%s/EUSTACE/derived/ensemble-daily" % \
                                os.getenv('SCRATCH')

# Array to store the sample in
ndata=numpy.ma.array(numpy.zeros(((2016-1850)*12,720)),mask=False)
dts=[]
# Assemble the sample slice by slice
for year in range(1850,2016):
    for month in range(1,13):
        t=(year-1850)*12+month-1
        dfile = "%s/%04d%02d.pkl" % (slice_dir,year,month)
        with open(dfile, "rb") as f:
            dslice = pickle.load(f)
        ndata[t,:]=dslice[0,:]
        dts.append(datetime.datetime(year,month,15))

# Plot the resulting array as a 2d colourmap
fig=Figure(figsize=(19.2,6),              # Width, Height (inches)
           dpi=600,
           facecolor=(0.5,0.5,0.5,1),
           edgecolor=None,
           linewidth=0.0,
           frameon=False,                
           subplotpars=None,
           tight_layout=None)
canvas=FigureCanvas(fig)
matplotlib.rc('image',aspect='auto')

# Add a textured grey background
s=(2000,600)
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
                  xlim=((start+datetime.timedelta(days=1)).timestamp(),
                        (end-datetime.timedelta(days=1)).timestamp()),
                  ylim=(0,1))
ax.set_axis_off() 

ndata = numpy.transpose(ndata)
s=ndata.shape
y = numpy.linspace(0,1,s[0]+1)
x = [(a-datetime.timedelta(days=15)).timestamp() for a in dts]
x.append((dts[-1]+datetime.timedelta(days=15)).timestamp())
img = ax.pcolorfast(x,y,numpy.cbrt(ndata),
                        cmap='RdYlBu_r',
                        alpha=1.0,
                        vmin=-2.0,
                        vmax=2.0,
                        zorder=100)

fig.savefig('ensemble.png')

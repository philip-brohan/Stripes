#!/usr/bin/env python

# Make an extended climate-stripes image from HadCRUT5
# Monthly, resolved in latitude, sampling in longitude, sampling the ensemble.

import os
import iris
import iris.cube
import iris.coords
import iris.coord_systems
import numpy
import datetime

from pandas import qcut

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.lines import Line2D

start = datetime.datetime(1851, 1, 1, 0, 0)
end = datetime.datetime(2022, 12, 31, 23, 59)

from get_sample import get_sample_cube

# Regridded data resolution
def plot_cube(resolution,xmin=-180,xmax=180,
                         ymin=-90,ymax=90,
                         pole_latitude=90,
                         pole_longitude=180,
                         npg_longitude=0):

    cs=iris.coord_systems.RotatedGeogCS(pole_latitude,
                                        pole_longitude,
                                        npg_longitude)
    lat_values=numpy.arange(ymin,ymax+resolution,resolution)
    latitude = iris.coords.DimCoord(lat_values,
                                    standard_name='latitude',
                                    units='degrees_north',
                                    coord_system=cs)
    lon_values=numpy.arange(xmin,xmax+resolution,resolution)
    longitude = iris.coords.DimCoord(lon_values,
                                     standard_name='longitude',
                                     units='degrees_east',
                                     coord_system=cs)
    dummy_data = numpy.zeros((len(lat_values), len(lon_values)))
    plot_cube = iris.cube.Cube(dummy_data,
                               dim_coords_and_dims=[(latitude, 0),
                                                    (longitude, 1)])
    return plot_cube

# Load in batches or we'll run out of memory.
egrid=plot_cube(resolution=1)
rst = numpy.random.RandomState(seed=None)
dts=[]
ndata=None
for year in range(start.year,end.year+1,10):
    print("\n\n%4d\n\n" % year)
    ey = min(year+10,end.year)
    (ndyr,dtyr) = get_sample_cube(datetime.datetime(year,1,1,0,0),
                                  datetime.datetime(ey,12,31,23,59),
                                  new_grid=egrid,rstate=rst)
    dts.extend(dtyr)
    if ndata is None:
        ndata = ndyr
    else:
        ndata = numpy.ma.concatenate((ndata,ndyr))


# Plot the resulting array as a 2d colourmap
fig = Figure(
    figsize=(30, 20),  # Width, Height (inches)
    dpi=100,
    facecolor=(0.5, 0.5, 0.5, 1),
    edgecolor=None,
    linewidth=0.0,
    frameon=False,
    subplotpars=None,
    tight_layout=None,
)
canvas = FigureCanvas(fig)
matplotlib.rc("image", aspect="auto")


def add_latline(ax, latitude):
    latl = (latitude + 90) / 180
    ax.add_line(
        Line2D(
            [start.timestamp(), end.timestamp()],
            [latl, latl],
            linewidth=1.0,
            color=(0., 0., 0., 1),
            zorder=200,
        )
    )


# Add a textured grey background
s = (600, 400)
ax2 = fig.add_axes([0, 0.0, 1, 1], facecolor="green")
ax2.set_axis_off()  # Don't want surrounding x and y axis
nd2 = numpy.random.rand(s[1], s[0])
clrs = []
for shade in numpy.linspace(0.42 + 0.01, 0.36 + 0.01):
    clrs.append((shade, shade, shade, 1))
y = numpy.linspace(0, 1, s[1])
x = numpy.linspace(0, 1, s[0])
img = ax2.pcolormesh(
    x,
    y,
    nd2,
    cmap=matplotlib.colors.ListedColormap(clrs),
    alpha=1.0,
    shading="gouraud",
    zorder=10,
)

s=ndata.shape
mask=ndata.mask
ndata=qcut(ndata.flatten(),200,labels=False,duplicates='drop').reshape(s)
ndata = numpy.ma.masked_array(data=ndata,mask=mask)

# Plot the stripes
ax = fig.add_axes(
    [0, 0.0, 1, 1],
    facecolor="black",
    xlim=(
        (start + datetime.timedelta(days=1)).timestamp(),
        (end - datetime.timedelta(days=1)).timestamp(),
    ),
    ylim=(0, 1),
)
ax.set_axis_off()

ndata = numpy.transpose(ndata)
s = ndata.shape
y = numpy.linspace(0, 1, s[0] + 1)
x = [
    datetime.datetime.fromisoformat(
        (a - datetime.timedelta(days=15)).isoformat()
    ).timestamp()
    for a in dts
]
x.append(
    datetime.datetime.fromisoformat(
        (dts[-1] + datetime.timedelta(days=15)).isoformat()
    ).timestamp()
)
img = ax.pcolorfast(
    x, y, ndata, cmap="RdYlBu_r", alpha=1.0, zorder=100
)

for lat in [-60, -30, 0, 30, 60]:
    add_latline(ax, lat)

# Add a date grid
axg = fig.add_axes(
    [0, 0, 1, 1],
    facecolor="green",
    xlim=(
        (start + datetime.timedelta(days=1)).timestamp(),
        (end - datetime.timedelta(days=1)).timestamp(),
    ),
    ylim=(0, 1),
)
axg.set_axis_off()


def add_dateline(ax, year):
    x = datetime.datetime(year, 1, 1, 0, 0).timestamp()
    ax.add_line(
        Line2D([x, x], [0.0, 1.0], linewidth=1, color=(0, 0, 0, 1), zorder=200)
    )


for year in range(1860, 2030, 10):
    add_dateline(axg, year)

fig.savefig("decal.png")

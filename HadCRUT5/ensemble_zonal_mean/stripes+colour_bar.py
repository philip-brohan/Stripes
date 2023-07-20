#!/usr/bin/env python

# Make an extended climate-stripes image from HadCRUT5
# Monthly, resolved in latitude, sampling in longitude, sampling the ensemble.
# Adds a colour bar & latitude axis - for formal use.

import os
import sys
import iris
import numpy
import datetime

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D
from matplotlib.colors import BoundaryNorm

start = datetime.datetime(1851, 1, 1, 0, 0)
end = datetime.datetime(2022, 12, 31, 23, 59)

from get_sample import get_sample_cube

(ndata, dts) = get_sample_cube(start, end)

# Plot the resulting array as a 2d colourmap
fig = Figure(
    figsize=(16, 4.5),  # Width, Height (inches)
    dpi=200,
    facecolor=(0.5, 0.5, 0.5, 1),
    edgecolor=None,
    linewidth=0.0,
    frameon=False,
    subplotpars=None,
    tight_layout=None,
)
canvas = FigureCanvas(fig)
matplotlib.rc("image", aspect="auto")

# White background
axb = fig.add_axes(
    [0.0, 0.0, 1.0, 1.0],
    facecolor="white",
    xmargin=0,
    ymargin=0,
)
axb.set_axis_off()
axb.fill([0, 1, 1, 0], [0, 0, 1, 1], "white")


def add_latline(ax, latitude):
    latl = (latitude + 90) / 180
    ax.add_line(
        Line2D(
            [start.timestamp(), end.timestamp()],
            [latl, latl],
            linewidth=0.75,
            color=(0.2, 0.2, 0.2, 1),
            zorder=200,
        )
    )


# Add a textured grey background
s = (2000, 100)
ax2 = fig.add_axes([0.0, 0.05, 0.9, 0.95], facecolor="green")
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

# Plot the stripes
ax = fig.add_axes(
    [0.0, 0.05, 0.9, 0.95],
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
levels=[-5, -2, -1, -0.5, -0.2, 0.2, 0.5, 1, 2, 5]
cmap=matplotlib.colormaps["RdYlBu_r"]
img = ax.pcolorfast(
    x,
    y,
    ndata,
    norm=BoundaryNorm(levels,ncolors=cmap.N, clip=True),
    cmap=cmap,
    zorder=100,
)

# Add a latitude grid
for lat in [-60, -30, 0, 30, 60]:
    add_latline(ax, lat)

# Add a date grid
axg = fig.add_axes(
    [0.0, 0, 0.9, 1],
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
        Line2D(
            [x, x], [0.04, 1.0], linewidth=0.75, color=(0.2, 0.2, 0.2, 1), zorder=200
        )
    )
    ax.text(
        x,
        0.025,
        "%04d" % year,
        horizontalalignment="center",
        verticalalignment="center",
        color="black",
        size=12,
        clip_on=True,
        zorder=200,
    )


for year in range(1860, 2023, 10):
    add_dateline(axg, year)

# ColourBar
ax_cb = fig.add_axes([0.925, 0.06125, 0.05, 0.9])
ax_cb.set_axis_off()
cb = fig.colorbar(
    img,
    ax=ax_cb,
    location="right",
    orientation="vertical",
    fraction=1.0,
    ticks = levels,
    label="Anomaly (\N{degree sign}C)",
)


fig.savefig("HadCRUT5+cb.png")

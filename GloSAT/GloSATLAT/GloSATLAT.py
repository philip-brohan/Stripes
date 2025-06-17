#!/usr/bin/env python

# GloSAT LAT stripes - anomalies.
# Monthly, resolved in latitude,

import iris
import iris.coord_systems
import iris.fileformats

coord_s = iris.coord_systems.GeogCS(iris.fileformats.pp.EARTH_RADIUS)

# I don't want warnings about sub-second time precision
iris.FUTURE.date_microseconds = True

import datetime
import numpy as np

from utilities.utils import longitude_reduce, csmooth
from utilities.grids import VRCube

from GloSAT.GloSATLAT.load import load_month, get_land_mask


import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
import matplotlib.colors as colors


import argparse


class LinkedArgumentsAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        # Check if the linked argument exists when this one is set
        if option_string == "--lat_resolution" and not hasattr(
            namespace, "lon_resolution"
        ):
            parser.error(
                "--lon_resolution must be specified when --lat_resolution is used"
            )
        elif option_string == "--lon_resolution" and not hasattr(
            namespace, "lat_resolution"
        ):
            parser.error(
                "--lat_resolution must be specified when --lon_resolution is used"
            )


parser = argparse.ArgumentParser()
parser.add_argument(
    "--reduce",
    help="Longitude reduction method",
    type=str,
    required=False,
    default="sample",
)
parser.add_argument(
    "--convolve", help="Convolution filter", type=str, required=False, default="none"
)
parser.add_argument(
    "--vmin",
    type=float,
    required=False,
    default=-3.0,
)
parser.add_argument(
    "--vmax",
    type=float,
    required=False,
    default=3.0,
)
parser.add_argument(
    "--startyear",
    type=int,
    required=False,
    default=1950,
)
parser.add_argument(
    "--endyear",
    type=int,
    required=False,
    default=2025,
)
parser.add_argument(
    "--lat_resolution",
    type=float,
    required=False,
    default=None,
    action=LinkedArgumentsAction,
)
parser.add_argument(
    "--lon_resolution",
    type=float,
    required=False,
    default=None,
    action=LinkedArgumentsAction,
)
args = parser.parse_args()

start = datetime.datetime(args.startyear, 1, 1, 0, 0)
end = datetime.datetime(args.endyear, 12, 31, 23)

new_grid = None
if args.lat_resolution is not None:
    new_grid = VRCube(
        lat_resolution=args.lat_resolution, lon_resolution=args.lon_resolution
    )

land_mask = get_land_mask(new_grid=new_grid)

# Load the data for each month and reduce member and meridional variation
dts = []
ndata = None

for year in range(start.year, end.year + 1):
    print(year)
    for month in range(1, 13):
        dts.append(datetime.datetime(year, month, 15, 0))
        mdata = load_month(year, month, new_grid=new_grid)
        if mdata is None:
            ndmo = np.ma.MaskedArray(np.full((land_mask.shape[0], 1), np.nan), True)
        else:
            mdata.data.data[mdata.data.mask] = np.nan  # Mask the data
            ndmo = longitude_reduce(args.reduce, mdata.data, mask=land_mask.data.mask)
        if ndata is None:
            ndata = ndmo
        else:
            ndata = np.concatenate((ndata.data, ndmo.data), axis=1)
    ndata = np.ma.MaskedArray(ndata.data, np.isnan(ndata.data))

# # Filter
if args.convolve != "none":
    ndata = csmooth(args.convolve, ndata)

# Set the colours
cmap = matplotlib.colormaps.get_cmap("RdYlBu_r")
# Set levels so there's an equal amount of each colour
levels = np.quantile(
    ndata.compressed(),
    np.linspace(0, 1, cmap.N + 1),
    method="linear",
)
norm = colors.BoundaryNorm(levels, cmap.N)

# Plot the resulting array as a 2d colourmap
fig = Figure(
    figsize=(16, 4.5),  # Width, Height (inches)
    dpi=300,
    facecolor=(0.5, 0.5, 0.5, 1),
    edgecolor=None,
    linewidth=0.0,
    frameon=False,
    subplotpars=None,
    tight_layout=None,
)
font = {"size": 12}
matplotlib.rc("font", **font)
canvas = FigureCanvas(fig)
matplotlib.rc("image", aspect="auto")

# White background for whole figure
axb = fig.add_axes(
    [0.0, 0.0, 1.0, 1.0],
    facecolor="white",
    xmargin=0,
    ymargin=0,
)
axb.set_axis_off()
axb.fill([0, 1, 1, 0], [0, 0, 1, 1], "white")

# Add a textured grey background
s = (2000, 600)
ax2 = fig.add_axes([0.0, 0.05, 0.9, 0.95], facecolor="green")
ax2.set_axis_off()
nd2 = np.random.rand(s[1], s[0])
clrs = []
for shade in np.linspace(0.42 + 0.01, 0.36 + 0.01):
    clrs.append((shade, shade, shade, 1))
y = np.linspace(0, 1, s[1])
x = np.linspace(0, 1, s[0])
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
    ylim=(1, 0),
)
ax.set_axis_off()

s = ndata.shape
y = 1.0 - np.linspace(0, 1, s[0] + 1)
x = [(a - datetime.timedelta(days=15)).timestamp() for a in dts]
x.append((dts[-1] + datetime.timedelta(days=15)).timestamp())
img = ax.pcolorfast(x, y, ndata, cmap=cmap, alpha=1.0, norm=norm, zorder=100)

# Add a latitude grid
axg = fig.add_axes(
    [0.0, 0.05, 0.9, 0.95],
    facecolor="green",
    xlim=(
        (start + datetime.timedelta(days=1)).timestamp(),
        (end - datetime.timedelta(days=1)).timestamp(),
    ),
    ylim=(0, 1),
)
axg.set_axis_off()


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


for lat in (-60, -30, 0, 30, 60):
    add_latline(axg, lat)

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
    if (
        year >= args.startyear + 5 and year <= args.endyear - 5
    ):  # No space for label at the edges
        # Add the year label
        ax.text(
            x,
            0.024,
            "%04d" % year,
            horizontalalignment="center",
            verticalalignment="center",
            color="black",
            clip_on=True,
            zorder=200,
        )


for year in range((args.startyear // 10) * 10, args.endyear, 10):
    if year == args.startyear or year == args.endyear:
        continue
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
    label="Anomaly (C)",
    ticks=[-2, -1, -0.5, 0, 0.5, 1, 2],
)

fig.savefig("%s/%s_%s_%s.png" % (".", "GloSATLAT", args.reduce, args.convolve))

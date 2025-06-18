#!/usr/bin/env python

# GloSAT stripes - anomalies.
# Monthly, resolved in latitude,
# Comparison plot: MAT, LAT, and blended

import os
import sys
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
from utilities.plot import add_latline, get_colorbar_location, texture_background

from GloSAT.load import load_month as load_blended
from GloSAT.GloSATMAT.load import load_month as load_mat
from GloSAT.GloSATLAT.load import load_month as load_lat
from GloSAT.GloSATLAT.load import get_land_mask as get_lat_land_mask
from GloSAT.GloSATMAT.load import get_land_mask as get_mat_land_mask

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
lat_land_mask = get_lat_land_mask(new_grid=new_grid)
mat_land_mask = get_mat_land_mask(new_grid=new_grid)


# Load the data for each month and reduce member and meridional variation
dts_lat = []
dts_mat = []
dts_blended = []
ndata_lat = None
ndata_mat = None
ndata_blended = None

for year in range(start.year, end.year + 1):
    print(year)
    for month in range(1, 13):
        # LAT
        dts_lat.append(datetime.datetime(year, month, 15, 0))
        mdata = load_lat(year, month, new_grid=new_grid)
        if mdata is None:
            ndmo = np.ma.MaskedArray(np.full((lat_land_mask.shape[0], 1), np.nan), True)
        else:
            mdata.data.data[mdata.data.mask] = np.nan  # Mask the data
            ndmo = longitude_reduce(
                args.reduce, mdata.data, mask=lat_land_mask.data.mask
            )
        if ndata_lat is None:
            ndata_lat = ndmo
        else:
            ndata_lat = np.concatenate((ndata_lat.data, ndmo.data), axis=1)
            ndata_lat = np.ma.MaskedArray(ndata_lat.data, np.isnan(ndata_lat.data))
        # MAT
        dts_mat.append(datetime.datetime(year, month, 15, 0))
        mdata = load_mat(year, month, new_grid=new_grid)
        if mdata is None:
            ndmo = np.ma.MaskedArray(np.full((mat_land_mask.shape[0], 1), np.nan), True)
        else:
            mdata.data.data[mdata.data.mask] = np.nan  # Mask the data
            ndmo = longitude_reduce(args.reduce, mdata.data)
        if ndata_mat is None:
            ndata_mat = ndmo
        else:
            ndata_mat = np.concatenate((ndata_mat.data, ndmo.data), axis=1)
            ndata_mat = np.ma.MaskedArray(ndata_mat.data, np.isnan(ndata_mat.data))
        # Blended
        dts_blended.append(datetime.datetime(year, month, 15, 0))
        mdata = load_blended(year, month, new_grid=new_grid)
        if mdata is None:
            ndmo = np.ma.MaskedArray(np.full((mat_land_mask.shape[0], 1), np.nan), True)
        else:
            mdata.data.data[mdata.data.mask] = np.nan  # Mask the data
            ndmo = longitude_reduce(args.reduce, mdata.data)
        if ndata_blended is None:
            ndata_blended = ndmo
        else:
            ndata_blended = np.concatenate((ndata_blended.data, ndmo.data), axis=1)
            ndata_blended = np.ma.MaskedArray(
                ndata_blended.data, np.isnan(ndata_blended.data)
            )

# # Filter
if args.convolve != "none":
    ndata_lat = csmooth(args.convolve, ndata_lat)
    ndata_mat = csmooth(args.convolve, ndata_mat)
    ndata_blended = csmooth(args.convolve, ndata_blended)

# Set the colours
cmap = matplotlib.colormaps.get_cmap("RdYlBu_r")
# Set levels so there's an equal amount of each colour
lat_levels = np.quantile(
    ndata_lat.compressed(),
    np.linspace(0, 1, cmap.N + 1),
    method="linear",
)
lat_norm = colors.BoundaryNorm(lat_levels, cmap.N)
mat_levels = np.quantile(
    ndata_mat.compressed(),
    np.linspace(0, 1, cmap.N + 1),
    method="linear",
)
mat_norm = colors.BoundaryNorm(mat_levels, cmap.N)
blended_levels = np.quantile(
    ndata_blended.compressed(),
    np.linspace(0, 1, cmap.N + 1),
    method="linear",
)
blended_norm = colors.BoundaryNorm(blended_levels, cmap.N)

# Plot the resulting arrays as 2d colourmaps
fig = Figure(
    figsize=(16 * 3, 4.5 * 3),  # Width, Height (inches)
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


# Plot the blended stripes
ax = fig.add_axes(
    [0.0, 0.02, 0.9, 0.95 / 3],
    facecolor="black",
    xlim=(
        (start + datetime.timedelta(days=1)).timestamp(),
        (end - datetime.timedelta(days=1)).timestamp(),
    ),
    ylim=(1, 0),
)
ax.set_axis_off()
# Add a textured grey background
img2 = texture_background(ax)

s = ndata_blended.shape
y = 1.0 - np.linspace(0, 1, s[0] + 1)
x = [(a - datetime.timedelta(days=15)).timestamp() for a in dts_blended]
x.append((dts_blended[-1] + datetime.timedelta(days=15)).timestamp())
img = ax.pcolorfast(
    x, y, ndata_blended, cmap=cmap, alpha=1.0, norm=blended_norm, zorder=100
)
ax_cb = fig.add_axes(get_colorbar_location(ax))

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


# Add a latitude grid
axg = fig.add_axes(
    [0.0, 0.02, 0.9, 0.98],
    facecolor="green",
    xlim=(
        (start + datetime.timedelta(days=1)).timestamp(),
        (end - datetime.timedelta(days=1)).timestamp(),
    ),
    ylim=(0, 1),
)
axg.set_axis_off()


for lat in (-60, -30, 0, 30, 60):
    add_latline(ax, lat, start, end)

# Plot the MAT data

ax_mat = fig.add_axes(
    [0.0, 0.02 + 1 / 3, 0.9, 0.95 / 3],
    facecolor="black",
    xlim=(
        (start + datetime.timedelta(days=1)).timestamp(),
        (end - datetime.timedelta(days=1)).timestamp(),
    ),
    ylim=(1, 0),
)
ax_mat.set_axis_off()

# Textured grey background
img3 = texture_background(ax_mat)


s = ndata_blended.shape
y = 1.0 - np.linspace(0, 1, s[0] + 1)
x = [(a - datetime.timedelta(days=15)).timestamp() for a in dts_blended]
x.append((dts_blended[-1] + datetime.timedelta(days=15)).timestamp())
img_m = ax_mat.pcolorfast(
    x, y, ndata_mat, cmap=cmap, alpha=1.0, norm=mat_norm, zorder=100
)
ax_cbm = fig.add_axes(get_colorbar_location(ax_mat))
ax_cbm.set_axis_off()
cbm = fig.colorbar(
    img_m,
    ax=ax_cbm,
    location="right",
    orientation="vertical",
    fraction=1.0,
    label="Anomaly (C)",
    ticks=[-2, -1, -0.5, 0, 0.5, 1, 2],
)

for lat in (-60, -30, 0, 30, 60):
    add_latline(ax_mat, lat, start, end)

# Plot the LAT data

ax_lat = fig.add_axes(
    [0.0, 0.02 + 2 / 3, 0.9, 0.95 / 3],
    facecolor="black",
    xlim=(
        (start + datetime.timedelta(days=1)).timestamp(),
        (end - datetime.timedelta(days=1)).timestamp(),
    ),
    ylim=(1, 0),
)
ax_lat.set_axis_off()

# Textured grey background
img4 = texture_background(ax_lat)


s = ndata_blended.shape
y = 1.0 - np.linspace(0, 1, s[0] + 1)
x = [(a - datetime.timedelta(days=15)).timestamp() for a in dts_blended]
x.append((dts_blended[-1] + datetime.timedelta(days=15)).timestamp())
img_l = ax_lat.pcolorfast(
    x, y, ndata_lat, cmap=cmap, alpha=1.0, norm=lat_norm, zorder=100
)
ax_cbl = fig.add_axes(get_colorbar_location(ax_lat))
ax_cbl.set_axis_off()
cbl = fig.colorbar(
    img_l,
    ax=ax_cbl,
    location="right",
    orientation="vertical",
    fraction=1.0,
    label="Anomaly (C)",
    ticks=[-2, -1, -0.5, 0, 0.5, 1, 2],
)

for lat in (-60, -30, 0, 30, 60):
    add_latline(ax_lat, lat, start, end)


# Add a date grid to the whole figure
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
            0.01,
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


fig.savefig("%s/%s_%s_%s.png" % (".", "SAT+MAT+Blended", args.reduce, args.convolve))

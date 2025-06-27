#!/usr/bin/env python

# HadCRUT stripes - anomalies.
# Monthly, resolved in latitude,
# Comparison plot: Three different ensemble members

import datetime
import numpy as np

from utilities.utils import longitude_reduce, csmooth
from utilities.grids import VRCube
from utilities.plot import plot_dataset

from GC5_Central.load import load_month, experiments

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
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
    default=None,
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

if args.endyear is None:
    args.endyear = datetime.datetime.now().year

start = datetime.datetime(args.startyear, 1, 1, 0, 0)
end = datetime.datetime(args.endyear, 12, 31, 23)

new_grid = None
if args.lat_resolution is not None:
    new_grid = VRCube(
        lat_resolution=args.lat_resolution, lon_resolution=args.lon_resolution
    )


# Load the data for each month and reduce member and meridional variation
dts = []
ndata_ex1 = None
ndata_ex2 = None
ndata_ex3 = None

for year in range(start.year, end.year + 1):
    print(year)
    for month in range(1, 13):
        dts.append(datetime.datetime(year, month, 15, 0))
        # First member
        mdata = load_month(year, month, new_grid=new_grid, experiments=[experiments[0]])
        ndmo = longitude_reduce(args.reduce, mdata.data)
        if ndata_ex1 is None:
            ndata_ex1 = ndmo
        else:
            ndata_ex1 = np.concatenate((ndata_ex1.data, ndmo.data), axis=1)
            ndata_ex1 = np.ma.MaskedArray(ndata_ex1.data, np.isnan(ndata_ex1.data))
        # Second member
        mdata = load_month(year, month, new_grid=new_grid, experiments=[experiments[1]])
        ndmo = longitude_reduce(args.reduce, mdata.data)
        if ndata_ex2 is None:
            ndata_ex2 = ndmo
        else:
            ndata_ex2 = np.concatenate((ndata_ex2.data, ndmo.data), axis=1)
            ndata_ex2 = np.ma.MaskedArray(ndata_ex2.data, np.isnan(ndata_ex2.data))
        # Third member
        mdata = load_month(year, month, new_grid=new_grid, experiments=[experiments[2]])
        ndmo = longitude_reduce(args.reduce, mdata.data)
        if ndata_ex3 is None:
            ndata_ex3 = ndmo
        else:
            ndata_ex3 = np.concatenate((ndata_ex3.data, ndmo.data), axis=1)
            ndata_ex3 = np.ma.MaskedArray(ndata_ex3.data, np.isnan(ndata_ex3.data))


# # Filter
if args.convolve != "none":
    ndata_ex1 = csmooth(args.convolve, ndata_ex1)
    ndata_ex2 = csmooth(args.convolve, ndata_ex2)
    ndata_ex3 = csmooth(args.convolve, ndata_ex3)

# Set the colours
cmap = matplotlib.colormaps.get_cmap("RdYlBu_r")
# Set levels so there's an equal amount of each colour
ex_levels = np.quantile(
    ndata_ex1.compressed(),
    np.linspace(0, 1, cmap.N + 1),
    method="linear",
)
ex_norm = colors.BoundaryNorm(ex_levels, cmap.N)

# Plot the resulting arrays as 2d colourmaps
fig = Figure(
    figsize=(16 * 3, 4.5 * 6),  # Width, Height (inches)
    dpi=300,
    facecolor=(1.0, 1.0, 1.0, 1),
    edgecolor=None,
    linewidth=0.0,
    frameon=True,
    subplotpars=None,
    tight_layout=None,
)
font = {"size": 12}
matplotlib.rc("font", **font)
canvas = FigureCanvas(fig)
matplotlib.rc("image", aspect="auto")


ax_ex3 = fig.add_axes([0, 0, 1, 1 / 3])
plot_dataset(
    ax_ex3,
    dts,
    ndata_ex3,
    cmap=cmap,
    norm=ex_norm,
    colorbar=False,
    ticks=True,
    ticks_fontsize=18,
    cm_fontsize=18,
)

ax_ex2 = fig.add_axes([0, (0.05 + 1) / 3, 1, 0.95 / 3])
plot_dataset(
    ax_ex2,
    dts,
    ndata_ex2,
    cmap=cmap,
    norm=ex_norm,
    colorbar=True,
    ticks=False,
    cm_fontsize=18,
)

ax_ex1 = fig.add_axes([0, (0.05 + 2) / 3, 1, 0.95 / 3])
plot_dataset(
    ax_ex1,
    dts,
    ndata_ex1,
    cmap=cmap,
    norm=ex_norm,
    colorbar=False,
    ticks=False,
    cm_fontsize=18,
)

fig.savefig("%s/%s_%s_%s.png" % (".", "Three_members", args.reduce, args.convolve))

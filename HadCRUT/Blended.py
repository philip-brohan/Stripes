#!/usr/bin/env python

# HadCRUT stripes - anomalies.
# Monthly, resolved in latitude,

import datetime
import numpy as np

from utilities.utils import longitude_reduce, csmooth
from utilities.grids import VRCube
from utilities.plot import plot_dataset

from HadCRUT.load import load_month

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
ndata = None

for year in range(start.year, end.year + 1):
    print(year)
    for month in range(1, 13):
        mdata = load_month(year, month, new_grid=new_grid)
        mdata.data.data[mdata.data.mask] = np.nan  # Mask the data
        dts.append(datetime.datetime(year, month, 15, 0))
        ndmo = longitude_reduce(args.reduce, mdata.data)
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


plot_dataset(
    fig.add_axes([0, 0, 1, 1]),
    dts,
    ndata,
    cmap=cmap,
    norm=norm,
    colorbar=True,
    ticks=True,
    ticks_fontsize=12,
    cm_fontsize=8,
)

fig.savefig("%s/%s_%s_%s.png" % (".", "HadCRUT5", args.reduce, args.convolve))

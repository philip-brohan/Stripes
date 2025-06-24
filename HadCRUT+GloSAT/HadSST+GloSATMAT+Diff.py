#!/usr/bin/env python

# Temperature stripes - anomalies.
# Monthly, resolved in latitude,
# Comparison plot: HadSST, GloSATMAT, and difference

import datetime
import numpy as np

from utilities.utils import longitude_reduce_paired, csmooth
from utilities.grids import VRCube
from utilities.plot import plot_dataset

from HadSST.load import load_month as load_month_hadsst, get_land_mask
from GloSAT.GloSATMAT.load import load_month as load_month_glosatmat

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

new_grid = VRCube(lat_resolution=5, lon_resolution=5)
if args.lat_resolution is not None:
    new_grid = VRCube(
        lat_resolution=args.lat_resolution, lon_resolution=args.lon_resolution
    )

land_mask = get_land_mask(new_grid=new_grid)


# Load the data for each month and reduce member and meridional variation
dts = []
ndata_hadsst = None
ndata_glosatmat = None
ndata_difference = None

for year in range(start.year, end.year + 1):
    print(year)
    for month in range(1, 13):
        dts.append(datetime.datetime(year, month, 15, 0))

        # Do the longitude_reduce together - so the two datasets sample from the same grid-point
        hdata = load_month_hadsst(year, month, new_grid=new_grid)
        hdata.data.data[hdata.data.mask] = np.nan  # Mask the data
        gdata = load_month_glosatmat(year, month, new_grid=new_grid)
        gdata.data.data[gdata.data.mask] = np.nan  # Mask the data

        ndmoh, ndmog = longitude_reduce_paired(
            args.reduce, hdata.data, gdata.data, mask=land_mask.data.mask
        )
        if ndata_hadsst is None:
            ndata_hadsst = ndmoh
        else:
            ndata_hadsst = np.concatenate((ndata_hadsst.data, ndmoh.data), axis=1)
            ndata_hadsst = np.ma.MaskedArray(
                ndata_hadsst.data, np.isnan(ndata_hadsst.data)
            )
        if ndata_glosatmat is None:
            ndata_glosatmat = ndmog
        else:
            ndata_glosatmat = np.concatenate((ndata_glosatmat.data, ndmog.data), axis=1)
            ndata_glosatmat = np.ma.MaskedArray(
                ndata_glosatmat.data, np.isnan(ndata_glosatmat.data)
            )

ndata_difference = ndata_hadsst - ndata_glosatmat

# # Filter
if args.convolve != "none":
    ndata_hadsst = csmooth(args.convolve, ndata_hadsst)
    ndata_glosatmat = csmooth(args.convolve, ndata_glosatmat)
    ndata_difference = csmooth(args.convolve, ndata_difference)

# Set the colours
cmap = matplotlib.colormaps.get_cmap("RdYlBu_r")
# Set levels so there's an equal amount of each colour
hadsst_levels = np.quantile(
    np.concatenate(
        (
            ndata_hadsst.compressed(),
            ndata_glosatmat.compressed(),
        )
    ),
    np.linspace(0, 1, cmap.N + 1),
    method="linear",
)
hadsst_norm = colors.BoundaryNorm(hadsst_levels, cmap.N)

# Plot the resulting arrays as 2d colourmaps
fig = Figure(
    figsize=(16 * 2, 9 * 2),  # Width, Height (inches)
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

ax_diff = fig.add_axes([0, 0, 1, 1 / 3])
plot_dataset(
    ax_diff,
    dts,
    ndata_difference,
    cmap=cmap,
    norm=hadsst_norm,
    colorbar=False,
    ticks=True,
    ticks_fontsize=18,
)

ax_glosatmat = fig.add_axes([0, (0.05 + 1) / 3, 1, 0.95 / 3])
plot_dataset(
    ax_glosatmat,
    dts,
    ndata_glosatmat,
    cmap=cmap,
    norm=hadsst_norm,
    colorbar=True,
    ticks=False,
    cm_fontsize=18,
)

ax_hadsst = fig.add_axes([0, (0.05 + 2) / 3, 1, 0.95 / 3])
plot_dataset(
    ax_hadsst,
    dts,
    ndata_hadsst,
    cmap=cmap,
    norm=hadsst_norm,
    colorbar=False,
    ticks=False,
)

fig.savefig(
    "%s/%s_%s_%s.png" % (".", "HadSST+GloSATMAT+Diff", args.reduce, args.convolve)
)

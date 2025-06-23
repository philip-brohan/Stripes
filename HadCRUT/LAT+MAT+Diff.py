#!/usr/bin/env python

# HadCRUT component stripes - anomalies.
# Monthly, resolved in latitude,
# Comparison plot: MAT, LAT, and difference

import datetime
import numpy as np

from utilities.utils import longitude_reduce, csmooth
from utilities.grids import VRCube
from utilities.plot import plot_dataset

from HadSST.load import load_month as load_mat
from CRUTEM.load import load_month as load_lat
from CRUTEM.load import get_land_mask as get_lat_land_mask
from HadSST.load import get_land_mask as get_mat_land_mask

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
lat_land_mask = get_lat_land_mask(new_grid=new_grid)
mat_land_mask = get_mat_land_mask(new_grid=new_grid)


# Load the data for each month and reduce member and meridional variation
dts = []
ndata_lat = None
ndata_mat = None
ndata_diff = None

for year in range(start.year, end.year + 1):
    print(year)
    for month in range(1, 13):
        dts.append(datetime.datetime(year, month, 15, 0))
        # LAT
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

ndata_diff = ndata_lat - ndata_mat

# # Filter
if args.convolve != "none":
    ndata_lat = csmooth(args.convolve, ndata_lat)
    ndata_mat = csmooth(args.convolve, ndata_mat)
    ndata_diff = csmooth(args.convolve, ndata_diff)

# Set the colours
cmap = matplotlib.colormaps.get_cmap("RdYlBu_r")
# Set levels so there's an equal amount of each colour
lat_levels = np.quantile(
    ndata_lat.compressed(),
    np.linspace(0, 1, cmap.N + 1),
    method="linear",
)
lat_norm = colors.BoundaryNorm(lat_levels, cmap.N)
# mat_levels = np.quantile(
#     ndata_mat.compressed(),
#     np.linspace(0, 1, cmap.N + 1),
#     method="linear",
# )
# mat_norm = colors.BoundaryNorm(mat_levels, cmap.N)
# blended_levels = np.quantile(
#     ndata_diff.compressed(),
#     np.linspace(0, 1, cmap.N + 1),
#     method="linear",
# )
# blended_norm = colors.BoundaryNorm(blended_levels, cmap.N)

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


ax_diff = fig.add_axes([0, 0, 1, 1 / 3])
plot_dataset(
    ax_diff,
    dts,
    ndata_diff,
    cmap=cmap,
    norm=lat_norm,
    colorbar=False,
    ticks=True,
    ticks_fontsize=18,
    cm_fontsize=18,
)

ax_mat = fig.add_axes([0, (0.05 + 1) / 3, 1, 0.95 / 3])
plot_dataset(
    ax_mat,
    dts,
    ndata_mat,
    cmap=cmap,
    norm=lat_norm,
    colorbar=True,
    ticks=False,
    cm_fontsize=18,
)

ax_lat = fig.add_axes([0, (0.05 + 2) / 3, 1, 0.95 / 3])
plot_dataset(
    ax_lat,
    dts,
    ndata_lat,
    cmap=cmap,
    norm=lat_norm,
    colorbar=False,
    ticks=False,
    cm_fontsize=18,
)

fig.savefig("%s/%s_%s_%s.png" % (".", "LAT+MAT+Diff", args.reduce, args.convolve))

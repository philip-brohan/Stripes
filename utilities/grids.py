# Define a utility Cube for high-resolution global grids.

import numpy as np

import iris
import iris.cube
import iris.util
import iris.analysis
import iris.analysis.cartography
import iris.coord_systems

import warnings

# I'm not that fussed about precise planetary geometry
warnings.filterwarnings("ignore", "Using DEFAULT_SPHERICAL_EARTH_RADIUS.")

# High-res cube (0.1x0.1 degrees)
resolution = 0.1
xmin = -180
xmax = 180
ymin = -90
ymax = 90
pole_latitude = 90
pole_longitude = 180
npg_longitude = 0
cs = iris.coord_systems.RotatedGeogCS(pole_latitude, pole_longitude, npg_longitude)
lat_values = np.arange(ymin, ymax + resolution, resolution)
latitude = iris.coords.DimCoord(
    lat_values, standard_name="grid_latitude", units="degrees_north", coord_system=cs
)
latitude.guess_bounds()
lon_values = np.arange(xmin, xmax, resolution)
longitude = iris.coords.DimCoord(
    lon_values, standard_name="grid_longitude", units="degrees_east", coord_system=cs
)
longitude.guess_bounds()
dummy_data = np.ma.MaskedArray(np.zeros((len(lat_values), len(lon_values))), False)

HRCube = iris.cube.Cube(dummy_data, dim_coords_and_dims=[(latitude, 0), (longitude, 1)])
HRCube_grid_areas = iris.analysis.cartography.area_weights(HRCube)
HRCube_latitude_areas = np.mean(HRCube_grid_areas, axis=1)
HRCube_scs = cs


def VRCube(lat_resolution=1.0, lon_resolution=1.0):
    xmin = -180
    xmax = 180
    ymin = -90
    ymax = 90
    pole_latitude = 90
    pole_longitude = 180
    npg_longitude = 0
    cs = iris.coord_systems.RotatedGeogCS(pole_latitude, pole_longitude, npg_longitude)
    lat_values = np.arange(ymin, ymax + lat_resolution, lat_resolution)
    latitude = iris.coords.DimCoord(
        lat_values,
        standard_name="grid_latitude",
        units="degrees_north",
        coord_system=cs,
    )
    latitude.guess_bounds()
    lon_values = np.arange(xmin, xmax, lon_resolution)
    longitude = iris.coords.DimCoord(
        lon_values,
        standard_name="grid_longitude",
        units="degrees_east",
        coord_system=cs,
    )
    longitude.guess_bounds()
    dummy_data = np.ma.MaskedArray(
        np.full([len(lat_values), len(lon_values)], np.nan), True
    )

    VRCube = iris.cube.Cube(
        dummy_data, dim_coords_and_dims=[(latitude, 0), (longitude, 1)]
    )
    return VRCube

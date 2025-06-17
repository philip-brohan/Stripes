# Functions to load the GloSATLAT data

# Loading the data month-by-month is too slow, so we load a decade at a time and cache it

import iris
import numpy as np

import iris.coord_systems
import iris.fileformats

coord_s = iris.coord_systems.GeogCS(iris.fileformats.pp.EARTH_RADIUS)

from utilities.utils import rng

# I don't want warnings about sub-second time precision
iris.FUTURE.date_microseconds = True


current_decade = None
decadal = None
cached_grid = None


# Need a land mask - masks out ocean-only grid cells - keep cells with a small island.
def get_land_mask(new_grid=None):
    lm = iris.load_cube(
        "/data/users/hadobs/cma_datasets/hadcrut5/hadobs-release/HadCRUT.5.0.2.0-202502/analysis/HadCRUT.5.0.2.0.land_fraction.nc"
    )
    lm.coord("latitude").coord_system = coord_s
    lm.coord("longitude").coord_system = coord_s
    if new_grid is not None:
        lm = lm.regrid(new_grid, iris.analysis.Nearest())
    lm.data = np.ma.MaskedArray(
        lm.data.data, lm.data.data == 0.0
    )  # Mask out land fraction of 0
    return lm


def load_decade(year, new_grid=None):
    m = iris.load_cube(
        "/data/scratch/philip.brohan/GLOSAT/1.0/" + "GloSATLAT-1-0-0-0_anomalies.nc",
        iris.Constraint(
            time=lambda cell: cell.point.year >= year and cell.point.year < year + 10
        ),
    )
    m.coord("latitude").coord_system = coord_s
    m.coord("longitude").coord_system = coord_s
    m.data.data[m.data.mask] = np.nan  # Mask the data
    if new_grid is not None:
        m = m.regrid(new_grid, iris.analysis.Nearest())
    # Pick a random member at each gridpoint
    return m


# Load the data for a month
def load_month(year, month, new_grid=None):

    global current_decade
    global decadal
    global cached_grid
    # If the decade has changed, or the grid has changed, reload the decade
    try:
        if (
            current_decade is None
            or year < current_decade
            or year >= current_decade + 10
            or cached_grid != new_grid
        ):
            cached_grid = new_grid
            current_decade = year - (year % 10)
            decadal = load_decade(current_decade, new_grid=new_grid)
        m = decadal.extract(
            iris.Constraint(
                time=lambda cell: cell.point.year == year and cell.point.month == month
            ),
        )
    except (iris.exceptions.ConstraintMismatchError, AttributeError) as e:
        return new_grid
    if m is None:
        return new_grid
    return m

# Functions to load the GLOSAT data

# Loading the data month-by-month is too slow, so we load a decade at a time and cache it

import iris
import numpy as np

import iris.coord_systems
import iris.fileformats

coord_s = iris.coord_systems.GeogCS(iris.fileformats.pp.EARTH_RADIUS)

from utilities.utils import rng

# I don't want warnings about sub-second time precision
iris.FUTURE.date_microseconds = True

# Choose ten ensemble members - same as HadCRUT
members = (1, 2, 3, 4, 5, 56, 57, 58, 59, 60)


current_decade = None
decadal = None
cached_grid = None


# Load the data for a decade
def load_decade(year, new_grid=None):
    h = []
    for member in members:
        m = iris.load_cube(
            "/data/scratch/philip.brohan/GLOSAT/1.0/"
            + "GloSATref-1-0-0-0_analysis_anomalies_%d.nc" % member,
            iris.Constraint(
                time=lambda cell: cell.point.year >= year
                and cell.point.year < year + 10
            ),
        )
        m.coord("latitude").coord_system = coord_s
        m.coord("longitude").coord_system = coord_s
        m.data.data[m.data.mask] = np.nan  # Mask the data
        if new_grid is not None:
            m = m.regrid(new_grid, iris.analysis.Nearest())
        h.append(m)
    # Pick a random member at each gridpoint
    member = rng.integers(0, len(members), size=h[0].data.shape)
    for i in range(len(members)):
        h[0].data[member == i] = h[i].data[member == i]
    return h[0]


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

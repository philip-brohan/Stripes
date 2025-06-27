# Functions to load the GC5 data

# Loading the data month-by-month is too slow, so we load a decade at a time and cache it

import iris
import numpy as np

from utilities.utils import rng

# I don't want warnings about sub-second time precision
iris.FUTURE.date_microseconds = True

experiments = ["dl339", "dl340", "dl341"]

current_year = None
annual = None
cached_grid = None

climatology = iris.load_cube(
    "/data/scratch/philip.brohan/GC5-Central/Historical/climatology_1961-1990.nc"
)

default_grid = climatology.collapsed("time", iris.analysis.MEAN)
default_grid.data.fill(np.nan)  # Fill with NaNs to avoid issues with masked data
default_grid.data = np.ma.MaskedArray(
    default_grid.data.data, np.isnan(default_grid.data.data)
)  # Mask the data


# Need a land mask - masks out land-only grid cells
def get_land_mask(new_grid=None):
    lm = iris.load_cube(
        "/data/users/philip.brohan/fixed_fields/land_mask/opfc_global_2019.nc"
    )
    if new_grid is not None:
        lm = lm.regrid(new_grid, iris.analysis.Nearest())
    else:
        data_grid = load_year(1850, experiments=[experiments[0]])
        lm = lm.regrid(data_grid, iris.analysis.Nearest())
    lm.data = np.ma.MaskedArray(
        lm.data.data, lm.data.data == 0.0
    )  # Mask out land fraction of 0
    return lm


# Only want the regular monthly average data
MAconstraint = iris.Constraint(
    cube_func=lambda cube: any(cm.intervals[0] == "6 hour" for cm in cube.cell_methods)
)


# Load the data for a year
def load_year(year, new_grid=None):
    h = {}
    for experiment in experiments:
        m = iris.load_cube(
            "/data/scratch/philip.brohan/GC5-Central/Historical/"
            + "%s/%04d.pp" % (experiment, year),
            MAconstraint,
        )
        m.data -= climatology.data  # Convert to anomalies
        m.data = np.ma.MaskedArray(
            m.data.data, m.data.data == np.nan
        )  # create the mask
        m.data.data[m.data.mask] = np.nan  # Mask the data
        if new_grid is not None:
            m = m.regrid(new_grid, iris.analysis.Nearest())
        h[experiment] = m
    return h


# Pick a sample from a subset of the experiments at each gridpoint
def sample_experiments(h, subset=experiments):
    result = h[experiments[0]].copy()
    experiment = np.random.choice(subset, size=result.data.shape)
    for expt in experiments:
        result.data[experiment == expt] = h[expt].data[experiment == expt]
    return result


# Load the data for a month
def load_month(year, month, new_grid=None, experiments=experiments):

    global current_year
    global annual
    global cached_grid
    # If the year has changed, or the grid has changed, reload the decade
    try:
        if current_year is None or year != current_year or cached_grid != new_grid:
            cached_grid = new_grid
            current_year = year
            annual = load_year(current_year, new_grid=new_grid)
        # Sample randomly from the chosen experiments
        e = sample_experiments(annual, subset=experiments)
        m = e.extract(
            iris.Constraint(
                time=lambda cell: cell.point.year == year and cell.point.month == month
            ),
        )
    except (iris.exceptions.ConstraintMismatchError, AttributeError, OSError) as e:
        if new_grid is None:
            new_grid = default_grid
        return new_grid
    if m is None:
        if new_grid is None:
            new_grid = default_grid
        return new_grid
    return m

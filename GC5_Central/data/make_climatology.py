#!/usr/bin/env python

# Model T2m is actuals, o make a 1961-90 average

import iris

iris.FUTURE.save_split_attrs = True
from GC5_Central.load import MAconstraint, experiments


def load_year(year, new_grid=None, experiment=None):
    m = iris.load_cube(
        "/data/scratch/philip.brohan/GC5-Central/Historical/"
        + "%s/%04d.pp" % (experiment, year),
        MAconstraint,
    )
    return m


count = 0
climatology = None
for experiment in experiments:
    for year in range(1961, 1991):
        m = load_year(year, experiment=experiment)
        if climatology is None:
            climatology = m.copy()
        else:
            climatology.data += m.data
        count += 1

climatology.data /= count  # Average over the years
climatology.rename("T2m climatology 1961-1990")
iris.save(
    climatology,
    "/data/scratch/philip.brohan/GC5-Central/Historical/climatology_1961-1990.nc",
)

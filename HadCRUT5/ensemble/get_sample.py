# Get the sample cube for HadCRUT5
# Monthly, resolved in latitude, sampling in longitude, sampling the ensemble.

import os
import iris
import iris.coord_systems
import iris.fileformats
import numpy as np
import datetime

coord_s = iris.coord_systems.GeogCS(iris.fileformats.pp.EARTH_RADIUS)


# I want the time coordinate as datetime, not cftime
def convert_single_time(cftime_obj):
    """Convert a single cftime object to datetime"""
    return datetime.datetime(
        cftime_obj.year,
        cftime_obj.month,
        cftime_obj.day,
        cftime_obj.hour,
        cftime_obj.minute,
        cftime_obj.second,
    )


# Create vectorized version
cftime_to_datetime = np.vectorize(convert_single_time)


def get_sample_cube(
    start=datetime.datetime(1851, 1, 1, 0, 0),
    end=datetime.datetime(2018, 12, 31, 23, 59),
    climatology=None,
    new_grid=None,
    rstate=None,
):
    # Choose ten ensemble members (Should be half odd and half even,
    #   and half from 1-50, half from 51-100)
    members = (1, 2, 3, 4, 5, 56, 57, 58, 59, 60)

    # Might want the longitude random sampling to be reproducible
    if rstate is None:
        r_long = np.random.RandomState(seed=None)
    else:
        r_long = rstate
    # The ensemble random sampling need not be reproducible
    r_ensemble = np.random.RandomState(seed=None)

    # Load the HadCRUT5 analysis data
    h = []
    for member in members:
        m = iris.load_cube(
            "/data/scratch/philip.brohan/HadCRUT/version_5.0.2.0/"
            + "HadCRUT.5.0.2.0.analysis.anomalies.%d.nc" % member,
            iris.Constraint(time=lambda cell: start <= cell.point <= end),
        )
        m.coord("latitude").coord_system = coord_s
        m.coord("longitude").coord_system = coord_s
        # It's an anomaly dataset, but we still sometimes need a climatology
        #  to re-base the anomalies to a different period.
        if climatology is not None:
            dts = m.coords("time")[0].units.num2date(m.coords("time")[0].points)
            for tidx in range(len(dts)):
                midx = dts[tidx].month - 1
                m.data[tidx, :, :] -= climatology[midx].data

        if new_grid is not None:
            m = m.regrid(new_grid, iris.analysis.Nearest())
        h.append(m)

    dts = h[0].coords("time")[0].units.num2date(h[0].coords("time")[0].points)
    dts = cftime_to_datetime(dts)

    # Pick a random longitude at each month
    s = h[0].data.shape
    ndata = np.ma.array(np.zeros((s[0], s[1])), mask=True)
    for t in range(s[0]):
        for lat in range(s[1]):
            member = r_ensemble.randint(len(members))
            rand_l = r_long.randint(0, s[2])
            ndata[t, lat] = h[member].data[t, lat, rand_l]

    return (ndata, dts)

# Utility functions for the Stripes plots

import re
import numpy as np
from astropy.convolution import convolve

rng = np.random.default_rng()

import warnings

warnings.filterwarnings("ignore", message=".*NaN values detected post convolution.*")


# Longitude reduction
def longitude_reduce(choice, ndata, mask=None):
    nd2d = np.squeeze(ndata)
    result = np.ma.masked_array(np.full([nd2d.shape[0], 1], np.nan))
    result[:] = np.ma.masked
    if mask is None:
        mask = np.full(nd2d.shape, False)
    if choice == "sample":
        for i in range(nd2d.shape[0]):  # Iterate over latitudes
            alat = nd2d[i, :]
            if len(alat) > 0:
                alat = alat[~mask[i, :]]
                if len(alat) > 0:
                    result[i, 0] = rng.choice(alat, size=1)[0]
                    if ~np.isnan(result[i, 0]):
                        result.mask[i, 0] = False
        return result
    if choice == "mean":
        nd2d.mask = np.ma.mask_or(nd2d.mask, mask)
        for i in range(nd2d.shape[0]):  # Iterate over latitudes
            alat = nd2d[i, :].compressed()
            if len(alat) > 0:
                result[i, 0] = np.mean(alat)
                result.mask[i, 0] = False
        return result
    raise Exception("Unsupported reduction choice %s" % choice)


# Convolution smoothing
def csmooth(choice, ndata):
    ndata[ndata.mask] = np.nan
    if choice[:3] == "sub":  # Want residual from smoothing
        n2 = csmooth(choice[4:], ndata)
        return ndata - n2 + 0.5
    if choice == "none":
        return ndata
    if choice == "annual":
        filter = np.full((1, 13), 1 / 13)
        op = convolve(ndata, filter, boundary="extend")
        op = np.ma.masked_array(op, np.isnan(op))
        return op
    result = re.search(r"(\d+)x(\d+)", choice)
    if result is not None:
        hv = int(result.groups()[0])
        vv = int(result.groups()[1])
        filter = np.full((vv, hv), 1 / (vv * hv))
        op = convolve(ndata, filter, boundary="extend")
        op = np.ma.masked_array(op, np.isnan(op))
        return op
    raise Exception("Unsupported convolution choice %s" % choice)

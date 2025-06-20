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


# Paired Longitude reduction - both datasets sample from the same grid point
def longitude_reduce_paired(choice, ndata1, ndata2, mask=None):
    nd2d1 = np.squeeze(ndata1)
    result1 = np.ma.masked_array(np.full([nd2d1.shape[0], 1], np.nan))
    result1[:] = np.ma.masked
    nd2d2 = np.squeeze(ndata2)
    result2 = result1.copy()
    if mask is None:
        mask = np.full(nd2d1.shape, False)
    if choice == "sample":
        for i in range(nd2d1.shape[0]):  # Iterate over latitudes
            alat1 = nd2d1[i, :]
            alat2 = nd2d2[i, :]
            if len(alat1) > 0:
                alat1 = alat1[~mask[i, :]]
                alat2 = alat2[~mask[i, :]]
                if len(alat1) > 0:
                    random_idx = rng.integers(0, len(alat1))
                    result1[i, 0] = alat1.data[random_idx]
                    result2[i, 0] = alat2.data[random_idx]
                    if ~np.isnan(result1[i, 0]):
                        result1.mask[i, 0] = False
                    if ~np.isnan(result2[i, 0]):
                        result2.mask[i, 0] = False
        return (result1, result2)
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

#!/usr/bin/env python

# Download the 20CRv3 monthly-mean T2m.

import os
import subprocess

base_url="ftp://ftp.cdc.noaa.gov/Datasets/20thC_ReanV3"

local_dir="%s/20CR/version_3/monthly_means" % os.getenv('SCRATCH')

remote = "%s/Monthlies/2mSI-MO/air.2m.mon.mean.nc" % base_url
local = "%s/air.2m.mon.mean.nc" % local_dir
if not os.path.exists(os.path.dirname(local)):
    os.makedirs(os.path.dirname(local))
if not os.path.isfile(local):
    cmd="wget -O %s %s" % (local,remote)
    wg_retvalue=subprocess.call(cmd,shell=True)
    if wg_retvalue!=0:
        raise Exception("Failed to retrieve data")

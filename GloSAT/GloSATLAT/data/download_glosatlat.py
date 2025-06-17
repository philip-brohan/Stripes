#!/usr/bin/env python

# Download the monthly GLOSAT_LAT data from CEDA

import os
import subprocess


base_url = (
    "https://dap.ceda.ac.uk/badc/deposited2025/" + "GloSAT/GloSATLAT-1-0-0-0/grids"
)

local_dir = "%s/GLOSAT/1.0/" % os.getenv("SCRATCH")

file_n = "GloSATLAT-1-0-0-0_anomalies.nc"
remote = "%s/%s?download=1" % (base_url, file_n)
local = "%s/%s" % (local_dir, file_n)
if not os.path.exists(os.path.dirname(local)):
    os.makedirs(os.path.dirname(local))
if not os.path.isfile(local):
    cmd = "wget -O %s %s" % (local, remote)
    wg_retvalue = subprocess.call(cmd, shell=True)
    # time.sleep(5)
    if wg_retvalue != 0:
        raise Exception("Failed to retrieve data")

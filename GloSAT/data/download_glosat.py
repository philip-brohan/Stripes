#!/usr/bin/env python

# Download the monthly GLOSAT_ref data from CEDA for a
#  specified period.

import os
import datetime
import subprocess


base_url = (
    "https://dap.ceda.ac.uk/badc/deposited2025/"
    + "GloSAT/GloSATref-1-0-0-0/analysis/grids/ensemble/"
)

local_dir = "%s/GLOSAT/1.0/" % os.getenv("SCRATCH")

for member in (1, 2, 3, 4, 5, 56, 57, 58, 59, 60):
    file_n = "GloSATref-1-0-0-0_analysis_anomalies_%d.nc" % member
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

#!/usr/bin/env python

# Download the monthly GLOSAT_MAT data from CEDA

import os
import subprocess


base_url = (
    "https://dap.ceda.ac.uk/badc/deposited2025/"
    + "GloSAT/GloSATMAT/ensemble/anom_1961_1990/"
)

local_dir = "%s/GLOSAT/1.0/" % os.getenv("SCRATCH")

for member in (1, 2, 3, 4, 5, 56, 57, 58, 59, 60):
    file_n = "GloSATMAT_2.4.0.0_ensemble_member_anomaly_%04d_b1961_1990.nc" % member
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

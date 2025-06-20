#!/usr/bin/env python

# Download the monthly HadSST3 data from Hadobs for a
#  specified period.

import os
import zipfile
import subprocess


base_url = "https://www.metoffice.gov.uk/hadobs/hadsst3/data/HadSST.3.1.1.0/netcdf/"

local_dir = "%s/HadSST/3.1.1.0/" % os.getenv("SCRATCH")

for member in ("1_to_10", "51_to_60"):
    file_n = "HadSST.3.1.1.0.anomalies.%s_netcdf.zip" % member
    remote = "%s/%s" % (base_url, file_n)
    local = "%s/%s" % (local_dir, file_n)
    if not os.path.exists(os.path.dirname(local)):
        os.makedirs(os.path.dirname(local))
    if not os.path.isfile(local):
        cmd = "wget -O %s %s" % (local, remote)
        wg_retvalue = subprocess.call(cmd, shell=True)
        # time.sleep(5)
        if wg_retvalue != 0:
            raise Exception("Failed to retrieve data")
    with zipfile.ZipFile(local, "r") as zip_ref:
        zip_ref.extractall(local_dir)

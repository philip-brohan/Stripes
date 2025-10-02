#!/usr/bin/env python

# Extract the Precipitation for all years for all three runs

import os


# Function to check if the job is already done for this timepoint
def is_done(run, year):
    op_file_name = ("%s/GC5-Central/Historical/%s/prate_%04d.pp") % (
        os.getenv("SCRATCH"),
        run,
        year,
    )
    if os.path.isfile(op_file_name):
        return True
    return False


for run in ("dl339", "dl340", "dl341"):
    for year in range(1850, 2015):
        if is_done(run, year):
            continue
        print("./get_prate_for_year.py --year=%d --run=%s" % (year, run))

#!/usr/bin/env python

# Scripts to make means for every month

import os
import datetime

for year in range (1850,2016):
    for month in range(1,13):
        opf = "%s/EUSTACE/1.0/monthly/%04d/%02d.nc" %\
                      (os.getenv('SCRATCH'),year,month)
        if not os.path.isfile(opf):
            print("./make_means_by_month.py --year=%d --month=%d" %
                    (year,month))

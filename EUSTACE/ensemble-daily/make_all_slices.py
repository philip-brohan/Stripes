#!/usr/bin/env python

# Scripts to make slices for every month

import os
import datetime

for year in range (1850,2016):
    for month in range (1,13):
        opf = "%s/EUSTACE/derived/ensemble-daily/%04d%02d.nc" %\
                      (os.getenv('SCRATCH'),year,month)
        if not os.path.isfile(opf):
            print("./make_slice.py --year=%d --month=%d" % (year,month) )

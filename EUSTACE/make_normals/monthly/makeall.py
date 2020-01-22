#!/usr/bin/env python

# Scripts to make normals for every month

import os
import datetime

for month in range(1,13):
    opf = "%s/EUSTACE/1.0/monthly/climatology_1961_1990/%02d.nc" %\
                  (os.getenv('SCRATCH'),month)
    if not os.path.isfile(opf):
        print("./make_normal_for_month.py --month=%d" % month )

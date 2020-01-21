#!/usr/bin/env python

# Scripts to make normals for every day

import os
import datetime

startyear=1969  # Any non leap year is fine

cdy = datetime.date(startyear,1,1)
while cdy.year==startyear:
    opf = "%s/EUSTACE/1.0/climatology_1961_1990/%02d%02d.nc" %\
                  (os.getenv('SCRATCH'),cdy.month,cdy.day)
    if not os.path.isfile(opf):
        print("./make_normal_for_day.py --month=%d --day=%d" %
                (cdy.month,cdy.day))
    cdy += datetime.timedelta(days=1)

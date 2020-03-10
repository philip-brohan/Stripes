#!/usr/bin/env python

# Scripts to make slices for every month

import os
import datetime

for year in range (1806,2016):
    print("./get_slice.py --year=%d" % year )

#!/usr/bin/env python

# Scripts to make slices for every month

import os
import datetime

for year in range (1979,2016):
    print("./make_comparison_slice.py --year=%d" % year )

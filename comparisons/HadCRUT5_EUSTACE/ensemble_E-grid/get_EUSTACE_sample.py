#!/usr/bin/env python

# Get a climate-stripes sample from Eustace
# Monthly, resolved in latitude, sampling in longitude, 
#   sampling across the ensemble.

import os
import sys
import numpy
import datetime
import pickle


start=datetime.datetime(1851,1,1,0,0)
end=datetime.datetime(2018,12,31,23,59)

sys.path.append('%s/../../../EUSTACE/ensemble-monthly/' % 
                                  os.path.dirname(__file__))
from get_sample import get_sample_cube

(ndata,dts) = get_sample_cube(start,end)

pickle.dump( (ndata,dts), open( "EUSTACE.pkl", "wb" ) )

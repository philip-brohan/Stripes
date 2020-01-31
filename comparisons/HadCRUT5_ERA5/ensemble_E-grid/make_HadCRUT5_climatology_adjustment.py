#!/usr/bin/env python

# Make an adjustment climatology to re-zero HadCRUT5 over 1981-2011
#  instead of 1961-90.

import os
import iris
import numpy
import pickle

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--opdir", help="Directory for output files",
                    default="%s/EUSTACE/derived/HadCRUT5_ERA5_comparison" % \
                                           os.getenv('SCRATCH'),
                    type=str,required=False)
args = parser.parse_args()
if not os.path.isdir(args.opdir):
    os.makedirs(args.opdir)


# Make the HadCRUT5 climatology adjustment (to 1981-2010 from 1961-90)
n=[]
for m in range(1,13):

    mc=iris.Constraint(time=lambda cell: cell.point.month == m and \
                                         cell.point.year > 1980 and \
                                         cell.point.year < 2011)
    members = (1,2,3,4,5,56,57,58,59,60)
    h = None
    for member in members:
        print("%d %d" % (m,member))
        mb = iris.load_cube("/scratch/hadcc/hadcrut5/build/HadCRUT5/analysis/"+
                     "HadCRUT.5.0.0.0.analysis.anomalies.%d.nc" % member,mc)
        if h is None:
            h = mb
        else:
            h.data += mb.data
    h.data /= 10
    n.append(h.extract(mc).collapsed('time', iris.analysis.MEAN))

dfile = "%s/HadCRUT5_climatology_adjustment.pkl" % args.opdir
pickle.dump( n, open( dfile, "wb" ) )

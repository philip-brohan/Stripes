#!/usr/bin/env python

# Make the 1961-1990 normals from EUSTACE1.0 monthly data 
#  for a given month.

import os
import iris

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--month", help="Integer month",
                    type=int,required=True)
parser.add_argument("--startyear", help="First year of climatology",
                    type=int,required=False,default=1961)
parser.add_argument("--endyear", help="First year of climatology",
                    type=int,required=False,default=1990)
args = parser.parse_args()

root_dir="%s/EUSTACE/1.0/" % os.getenv('SCRATCH')

op_dir = "%s/monthly/climatology_%04d_%04d" % (root_dir,args.startyear,args.endyear)
if not os.path.isdir(op_dir):
    os.makedirs(op_dir)

accum = None  
for cyr in range (args.startyear,args.endyear+1):
  inst = iris.load_cube("%s/monthly/%04d/%02d.nc" %
                          (root_dir,cyr,args.month),
                         'air_temperature')
  if accum is None:
      accum = inst
      count = inst.copy()
      count.data.mask = False
      count.data *= 0
      count.data[accum.data.mask==False] += 1
  else:
      accum.data.mask[inst.data.mask==False] = False
      accum.data[accum.data<0] *= 0
      accum.data = accum.data + inst.data
      count.data[inst.data.mask==False] += 1

accum.data[count.data>=20] /= count.data[count.data>=20]
accum.data.mask[count.data<20] = True

iris.save(accum,"%s/%02d.nc" % (op_dir,args.month),
          fill_value=-32768)

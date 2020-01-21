#!/usr/bin/env python

# Make monthly means from daily EUSTACE1.0 data.

import os
import iris
from calendar import monthrange

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--month", help="Integer month",
                    type=int,required=True)
parser.add_argument("--year", help="Integer year",
                    type=int,required=True)
args = parser.parse_args()

root_dir="%s/EUSTACE/1.0/" % os.getenv('SCRATCH')

op_dir = "%s/monthly/%04d" % (root_dir,args.year)
if not os.path.isdir(op_dir):
    os.makedirs(op_dir)

op_file = "%s/%02d.nc" % (op_dir,args.month)

def average_over_month(variable):
    accum = None  
    for dy in range (1,monthrange(args.year,args.month)[1]+1):
      inst = iris.load_cube("%s/%04d/tas_global_eustace_0_%04d%02d%02d.nc" %
                              (root_dir,args.year,args.year,
                               args.month,dy),
                             iris.Constraint(cube_func=(lambda c: c.var_name == variable)))
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
    return(accum)
    
avgs=[]
avgs.append(average_over_month('tas'))
for member in range(10):
    avgs.append(average_over_month('tasensemble_%d' % member))                       

iris.save(avgs,op_file,
          fill_value=-32768)

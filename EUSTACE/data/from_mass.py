#!/usr/bin/env python

# Retrieve the daily EUSTACE1.0 data from MASS

import os
import os.path
import datetime
import subprocess
import time
import tarfile
import afterburner.io.moose2 as moose

# Check moose availability
if not moose.has_moose_support():
    raise Exception("Moose unavailable")
if not moose.check_moose_commands_enabled(moose.MOOSE_LS):
    raise Exception("'moo ls' disabled")
if not moose.check_moose_commands_enabled(moose.MOOSE_GET):
    raise Exception("'moo get' disabled")

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--startyear",
                    type=int,required=False,
                    default=1850)
parser.add_argument("--endyear",
                    type=int,required=False,
                    default=2015)
args = parser.parse_args()

moose_dir=("moose://adhoc/users/philip.brohan/EUSTACE/1.0/")

local_dir="%s/EUSTACE/1.0/" % os.getenv('SCRATCH')
if not os.path.isdir(local_dir):
    os.makedirs(localdir)

def unarchive(year):
    tar_file="%s/%04d.tgz" % (local_dir,year)
    moose.get(os.path.dirname(tar_file),
              "%s/%s"% (moose_dir,os.path.basename(tar_file)))
    tf = tarfile.open(tar_file)
    tf.extractall(path=local_dir)
    # Update the extracted file times
    #  To stop SCRATCH deleting them as too old
    nfiles=os.listdir("%s/%04d" % (local_dir,year))
    for nfile in nfiles:
        os.utime("%s/%04d/%s" % (local_dir,year,nfile))
    os.remove(tar_file)
    

for year in range(args.startyear,args.endyear+1):
    if os.path.isfile("%s/%04d/tas_global_eustace_0_%04d0619.nc" % (
                        local_dir,year,year)): continue
    moose_file="%s/%04d.tgz" % (moose_dir,year)
    print(year)
    unarchive(year)

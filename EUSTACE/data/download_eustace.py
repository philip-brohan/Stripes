#!/usr/bin/env python

# Download the daily EUSTACE1.0 data from CEDA for a 
#  specified period.

import os
import datetime
import subprocess
import time

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--startyear",
                    type=int,required=False,
                    default=1850)
parser.add_argument("--endyear",
                    type=int,required=False,
                    default=2015)
args = parser.parse_args()

start=datetime.date(args.startyear,1,1)
end=datetime.date(args.endyear,12,31)

base_url=("http://dap.ceda.ac.uk/thredds/fileServer/"+
         "neodc/eustace/data/combined/mohc/eustace/"+
         "v1.0/day/0/0/R001400/20190326/global/")

local_dir="%s/EUSTACE/1.0/" % os.getenv('SCRATCH')

cday = start
while cday <= end:
    file_n= ("tas_global_eustace_0_%04d%02d%02d.nc" %
                  (cday.year,cday.month,cday.day))     
    remote = "%s/%04d/%s" % (base_url,cday.year,file_n)
    local = "%s/%04d/%s" % (local_dir,cday.year,file_n)
    if not os.path.exists(os.path.dirname(local)):
        os.makedirs(os.path.dirname(local))
    if not os.path.isfile(local):
        cmd="wget -O %s %s" % (local,remote)
        wg_retvalue=subprocess.call(cmd,shell=True)
        #time.sleep(5)
        if wg_retvalue!=0:
            raise Exception("Failed to retrieve data")
    cday = cday + datetime.timedelta(days=1)


#!/usr/bin/env python

# Backup the daily EUSTACE1.0 data to MASS

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
if not moose.check_moose_commands_enabled(moose.MOOSE_PUT):
    raise Exception("'moo put' disabled")

startyear=1850
endyear=2015

moose_dir=("moose://adhoc/users/philip.brohan/EUSTACE/1.0/")
if moose.run_moose_command('moo test %s' % moose_dir)[0]!='true':
# Make the moose directory
    moose.run_moose_command("moo mkdir -p %s" % moose_dir)

local_dir="%s/EUSTACE/1.0/" % os.getenv('SCRATCH')

def archive(year):
    tar_file="%s/%04d.tgz" % (local_dir,year)
    with tarfile.open(tar_file, "w:gz") as tar:
        tar.add("%s/%04d" % (local_dir,year), 
                 arcname="%04d" % year)
    moose.put(os.path.dirname(tar_file),
              [os.path.basename(tar_file)],
              moose_dir)
    os.remove(tar_file)
    

for year in range(startyear,endyear+1):
    moose_file="%s/%04d.tgz" % (moose_dir,year)
    if moose.run_moose_command('moo test %s' % moose_file)[0]!='true':
        print(year)
        archive(year)

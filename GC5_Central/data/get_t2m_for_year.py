#!/usr/bin/env python

# Get the GC5-Central historical run T2m for a given run and year

import os
from tempfile import NamedTemporaryFile
import subprocess

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--year", help="Year", type=int, required=True)
parser.add_argument("--run", help="Year", type=str, required=True)
parser.add_argument(
    "--opdir",
    help="Directory for output files",
    default="%s/GC5-Central/Historical" % os.getenv("SCRATCH"),
)
args = parser.parse_args()
opdir = "%s/%s" % (args.opdir, args.run)
if not os.path.isdir(opdir):
    os.makedirs(opdir)

print("%s %04d" % (args.run, args.year))

# Mass directory to use
mass_dir = "moose:/crum/u-%s/apm.pp/" % args.run

# Files to retrieve from
flist = []
for month in (
    "jan",
    "feb",
    "mar",
    "apr",
    "may",
    "jun",
    "jul",
    "aug",
    "sep",
    "oct",
    "nov",
    "dec",
):
    flist.append("%sa.pm%04d%s.pp" % (args.run, args.year, month))
# Create the query file
qfile = NamedTemporaryFile(mode="w+", delete=False)
qfile.write("begin_global\n")
qfile.write("   pp_file = (")
for ppfl in flist:
    qfile.write('"%s"' % ppfl)
    if ppfl != flist[-1]:
        qfile.write(",")
    else:
        qfile.write(")\n")
qfile.write("end_global\n")
qfile.write("begin\n")
qfile.write("    stash = 3236\n")
qfile.write("end\n")
qfile.close()

# Run the query
opfile = "%s/%04d.pp" % (opdir, args.year)
subprocess.call("moo select -C %s %s %s" % (qfile.name, mass_dir, opfile), shell=True)

os.remove(qfile.name)

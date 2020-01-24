#!/bin/bash

# Get the CMIP6 historical monthly tas for HadGEM3-GC31-LL
# Use managecmip - MO only.

# Get the monthly data
managecmip get -M cmip6 -e historical -t Amon -v tas -i MOHC -m HadGEM3-GC31-LL
# and the daily data
managecmip get -M cmip6 -e historical -t day -v tas -i MOHC -m HadGEM3-GC31-LL

# Make the data available on $SCRATCH
mkdir -p /scratch/hadpb/CMIP6/HadGEM3-GC31-LL/Historical
ln -s /project/champ/data/CMIP6/CMIP/MOHC/HadGEM3-GC31-LL/historical/*/Amon/tas/gn/v*/* /scratch/hadpb/CMIP6/HadGEM3-GC31-LL/Historical/
ln -s /project/champ/data/CMIP6/CMIP/MOHC/HadGEM3-GC31-LL/historical/*/day/tas/gn/v*/* /scratch/hadpb/CMIP6/HadGEM3-GC31-LL/Historical/

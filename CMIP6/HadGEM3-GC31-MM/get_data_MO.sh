#!/bin/bash

# Get the CMIP6 historical monthly tas for HadGEM3-GC31-MM
# Use managecmip - MO only.

# Get the monthly  data
managecmip get -M cmip6 -e historical -t Amon -v tas -i MOHC -m HadGEM3-GC31-MM

# same for daily data 
managecmip get -M cmip6 -e historical -t day -v tas -i MOHC -m HadGEM3-GC31-MM

# Make the data available on $SCRATCH
mkdir -p /scratch/hadpb/CMIP6/HadGEM3-GC31-MM/Historical
ln -s /project/champ/data/CMIP6/CMIP/MOHC/HadGEM3-GC31-MM/historical/*/Amon/tas/gn/v*/* /scratch/hadpb/CMIP6/HadGEM3-GC31-MM/Historical/
ln -s /project/champ/data/CMIP6/CMIP/MOHC/HadGEM3-GC31-MM/historical/*/day/tas/gn/v*/* /scratch/hadpb/CMIP6/HadGEM3-GC31-MM/Historical/

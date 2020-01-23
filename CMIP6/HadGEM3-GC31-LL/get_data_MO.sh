#!/bin/bash

# Get the CMIP6 historical monthly tas for HadGEM3-GC31-LL
# Use managecmip - MO only.

# List the avaialble data with 
# managecmip list -M cmip6 -e historical -t Amon -v tas -i MOHC -m HadGEM3-GC31-LL
# and get it with managecmip get.

# Make the data available on $SCRATCH
mkdir -p /scratch/hadpb/CMIP6/HadGEM3-GC31-LL/Historical
ln -s /project/champ/data/CMIP6/CMIP/MOHC/HadGEM3-GC31-LL/historical/*/Amon/tas/gn/v20190624/* /scratch/hadpb/CMIP6/HadGEM3-GC31-LL/Historical/

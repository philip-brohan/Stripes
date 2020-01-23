#!/bin/bash

# Get the CMIP6 historical monthly tas for UKESM1-0-LL
# Use managecmip - MO only.

# Get the monthly data
managecmip get -M cmip6 -e historical -t Amon -v tas -i MOHC -m UKESM1-0-LL
# and the daly data
managecmip get -M cmip6 -e historical -t day -v tas -i MOHC -m UKESM1-0-LL

# Make the data available on $SCRATCH
mkdir -p /scratch/hadpb/CMIP6/UKESM1-0-LL/Historical
ln -s /project/champ/data/CMIP6/CMIP/MOHC/UKESM1-0-LL/historical/*/Amon/tas/gn/v*/* /scratch/hadpb/CMIP6/UKESM1-0-LL/Historical/
ln -s /project/champ/data/CMIP6/CMIP/MOHC/UKESM1-0-LL/historical/*/day/tas/gn/v*/* /scratch/hadpb/CMIP6/UKESM1-0-LL/Historical/

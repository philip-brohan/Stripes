#!/bin/bash

montage ../../HadCRUT5/global-mean-annual-mean/HadCRUT5.png  ../../20CRv3/monthly_ensemble_mean/20CRv3.png ../../HadCRUT5/ensemble/HadCRUT5.png -tile 1x3 -geometry 1920x600+5+5 Stripes.png

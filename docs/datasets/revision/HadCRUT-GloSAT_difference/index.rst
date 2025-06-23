HadCRUT-GloSAT difference
==========================

.. figure:: ../../../../HadCRUT+GloSAT/HadCRUT+GloSAT+Diff_sample_3x3.png
   :width: 95%
   :align: center
   :figwidth: 95%

   Monthly temperature anomalies (w.r.t. 1961-90) from HadCRUT (top), GloSAT (middle), and their difference (bottom). In each case the vertical axis is latitude (south pole at the bottom, north pole at the top), and each pixel is from a randomly selected longitude and ensemble member. A 3x3 convolution is then applied. Grey areas show regions where the dataset has no data.

Note: In the land-sea comparison plots (:doc:`1 <../CRUTEM+HadSST+Difference/index>` & :doc:`2 <../GloSAT_land-sea_difference/index>`) the difference panel is the difference between the two plots above it, so the difference at any time:latitude point includes the effect of sampling a different longitude for each dataset (we can't choose the same longitude for land and sea because of their different coverages). But for the blended datasets it *is* possible to sample from the same longitude for each dataset, so we calculate the difference at all longitudes and sample that. This means that the difference is smaller than the difference between the two plots, but it's a more meaningful metric of the difference between the datasets.


.. toctree::
   :titlesonly:
   :maxdepth: 1

   Script to make the plot <./plot.rst>
   
For more details see the individual dataset versions:

.. toctree::
   :titlesonly:
   :maxdepth: 1

   HadCRUT <../HadCRUT/index>
   GloSAT <../GloSAT/index>



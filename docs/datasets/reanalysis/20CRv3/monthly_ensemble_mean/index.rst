20CRv3 monthly ensemble mean
============================

The `Twentieth Century Reanalysis <https://www.esrl.noaa.gov/psd/data/20thC_Rean/>`_, `version 3 <https://www.esrl.noaa.gov/psd/data/gridded/data.20thC_ReanV3.html>`_, provides ideal data for this sort of study: an 80-member ensemble, at about 0.25 degree resolution, every 3-hours back to 1836. Unfortunately, that's a 5Tb download, and the data is stored on tape in the US, so downloading is slow - getting it all would take weeks at best.

So instead I'm using the pre-processed data they helpfully provide. The monthly averages of the ensemble mean at 1-degree resolution. No ensemble - but exponentially more accessible.

.. figure:: ../../../../../20CRv3/monthly_ensemble_mean/20CRv3_E-grid.png
   :width: 95%
   :align: center
   :figwidth: 95%

   Monthly 2m-temperature anomalies (w.r.t. 1961-90) from the 20CRv3 ensemble mean (regridded to a 0.1 degree resolution. The vertical axis is latitude (south pole at the bottom, north pole at the top), and each pixel is from a randomly selected longitude.

.. toctree::
   :titlesonly:
   :maxdepth: 1

   Download the data <../data.rst>
   Script to make the plot <./plot.rst>
   Function to extract the data sample <./sample.rst>

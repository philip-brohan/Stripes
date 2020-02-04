ERA5 monthly ensemble (enda)
============================

The `ERA5 Reanalysis <https://www.ecmwf.int/en/forecasts/datasets/reanalysis-datasets/era5/>`_,  provides both a high-resolution flagship esitmate, and a 10-member ensemble, and is awesome as far as it goes. Unfortunately, as of Feb 2020, it only goes back to 1979 (an extension to 1950 is planned).

The reanalysis output is easily available, both hourly (3-hourly for the ensemble), and as monthly averages, from the `Copernicus Climate Data Store <https://cds.climate.copernicus.eu/>`_. Here, I'm using the monthly averages from the ensemble.

.. figure:: ../../../../../ERA5/monthly-ensemble/ERA5_E-grid.png
   :width: 95%
   :align: center
   :figwidth: 95%

   Monthly 2m-temperature anomalies (w.r.t. 1961-90) from the ERA5 enda ensembl (regridded to a 0.1 degree resolution. The vertical axis is latitude (south pole at the bottom, north pole at the top), and each pixel is from a randomly selected longitude and a randomly selected ensemble member.

.. toctree::
   :titlesonly:
   :maxdepth: 1

   Download the data <data.rst>
   Script to make the plot <./plot.rst>
   Function to extract the data sample <./sample.rst>

Observational dataset inter-comparison
--------------------------------------

:doc:`HadCRUT5 makes great stripes <./index>`, and it's a well-established and trustworthy source, but we should still check, if possible, against an alternative dataset. None of the possible alternatives are truely independent of HadCRUT - they all rely on historical land and sea thermometer observations, and there is a lot of overlap in the raw observations they use - but even so they can differ substantially in observation selection and processing, so a comparison is still of value.

I chose to compare against `EUSTACE <https://www.eustaceproject.org/>`_.

.. figure:: ../EUSTACE/ensemble-monthly/ensemble.png
   :width: 95%
   :align: center
   :figwidth: 95%

   Temperature anomalies (w.r.t. 1961-90) from the EUSTACE dataset after regridding to monthly resolution. The vertical axis is latitude (south pole at the bottom, north pole at the top), and each pixel is from a randomly selected longitude and ensemble member. Grey areas show regions where EUSTACE has no data. (:doc:`Figure source <datasets/observations/EUSTACE/ensemble-monthly/index>`).

This does look broadly similar to :doc:`the HadCRUT5 version <datasets/observations/HadCRUT5/ensemble/index>`. A detailed comparison confirms this agreement, but does reveal some interesting differences:

.. figure:: ../comparisons/HadCRUT5_EUSTACE/ensemble_E-grid/comparison_grid.png
   :width: 95%
   :align: center
   :figwidth: 95%

   At the top, the :doc:`extended stripes from HadCRUT5 <datasets/observations/HadCRUT5/ensemble/index>`. In the middle, the :doc:`extended stripes from EUSTACE <datasets/observations/EUSTACE/ensemble-monthly/index>`. At the bottom, the difference between them (HadCRUT5-EUSTACE). (:doc:`Figure source <datasets/comparisons/HadCRUT5_EUSTACE/ensemble_E-grid/index>`).

The two datasets agree about recent global warming, ENSO, and the mid-20th-century polar warming. There are obvious disagreements in the early 1850s, the early 1940s (in the low-latitudes) and at the latitude-extremes of the EUSTACE dataset
(even in recent years). To my eyes, these look more likely to be issues in EUSTACE than in HadCRUT, as we'd expect from the relative maturities of the two datasets.

It would be good to have a third opinion - let's try the :doc:`Twentieth Century Reanalysis (20CR) version 3 <datasets/reanalysis/20CRv3/monthly_ensemble_mean/index>`:

.. figure:: ../comparisons/HadCRUT5_20CRv3/H-ensemble_E-grid/comparison_grid.png
   :width: 95%
   :align: center
   :figwidth: 95%

   At the top, the :doc:`extended stripes from HadCRUT5 <datasets/observations/HadCRUT5/ensemble/index>`. In the middle, the :doc:`extended stripes from 20CRv3 <datasets/reanalysis/20CRv3/monthly_ensemble_mean/index>`. At the bottom, the difference between them (HadCRUT5-20CRv3). (:doc:`Figure source <datasets/comparisons/HadCRUT5_20CRv3/H-ensemble_E-grid/index>`).

--------------------------------------------

This document and the data associated with it are crown copyright (2019) and licensed under the terms of the `Open Government Licence <https://www.nationalarchives.gov.uk/doc/open-government-licence/version/2/>`_. All code included is licensed under the terms of the `GNU Lesser General Public License <https://www.gnu.org/licenses/lgpl.html>`_.

Get data sample for HadCRUT-20CRv3 comparison
=============================================

It's important to take a sample from the difference field, rather than differencing the two samples. So we take a field from both datasets at the same time, put them on the same grid, take the difference and extract a sample. That process can be slow (and take a lot of memory), so we'll do it in one year batches:

.. literalinclude:: ../../../../../comparisons/HadCRUT5_20CRv3/H-ensemble_E-grid/make_comparison_slice.py

Script to make the sample batch for each year:

.. literalinclude:: ../../../../../comparisons/HadCRUT5_20CRv3/H-ensemble_E-grid/make_all_slices.py

Script to combine the annual batches into a complete sample:


.. literalinclude:: ../../../../../comparisons/HadCRUT5_20CRv3/H-ensemble_E-grid/get_comparison_sample.py


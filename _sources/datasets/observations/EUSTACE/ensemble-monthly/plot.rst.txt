Stripes plotting code
=====================

Parallise the calculation by extracting the data sample for each year independently:

.. literalinclude:: ../../../../../EUSTACE/ensemble-monthly/make_slice.py

And then running that script for each year as a separate task:

.. literalinclude:: ../../../../../EUSTACE/ensemble-monthly/make_all_slices.py

Then assemble the slices to make the figure:

.. literalinclude:: ../../../../../EUSTACE/ensemble-monthly/stripes.py



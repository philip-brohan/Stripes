Make 1961-90 normals from monthly EUSTACE data
==============================================

The only complication in this process is in handling missing data. I chose (arbitrarily) that a monthly normal is the mean of all available monthly averages in the period 1961-90 if at least 20 monthly averages are available (and missing otherwise).

Parallelise the calculation by writing a script to do one month

.. literalinclude:: ../../../../../EUSTACE/make_normals/monthly/make_normal_for_month.py

and then making a task to run that script once for each month,

.. literalinclude:: ../../../../../EUSTACE/make_normals/monthly/makeall.py

and then running those tasks in parallel.

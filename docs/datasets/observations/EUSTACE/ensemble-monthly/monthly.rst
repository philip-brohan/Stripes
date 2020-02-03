Make monthly averages from daily EUSTACE data
=============================================

The only complication in this process is in handling missing data. I chose (arbitrarily) that a monthly average would be the mean of all the available daily averages in that month if at least 20 daily values were available (and missing otherwise).

166 years of daily data is a lot of averaging, so parallelise it by writing a script to do one month

.. literalinclude:: ../../../../../EUSTACE/make_monthly_averages/make_means_by_month.py

and then making a task to run that script once for each month in the period,

.. literalinclude:: ../../../../../EUSTACE/make_monthly_averages/makeall.py

and then running those tasks in parallel.

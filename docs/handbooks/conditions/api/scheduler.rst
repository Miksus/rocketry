
Scheduler
=========

Scheduler related conditions are often
useful for testing purposes to prevent
the scheduler running without exit.

Perhaps the most useful of such conditions is
``scheduler_running``. This condition is true
if the scheduler has been running more than 
given in ``more_than`` argument. There is also
an argument ``less_than`` to specify the maximum.

.. literalinclude:: /code/conds/api/scheduler.py
    :language: py
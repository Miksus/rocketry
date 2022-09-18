
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

.. literalinclude:: /code/conds/api/scheduler_running.py
    :language: py

There is also a condition ``scheduler_cycles`` that
also takes ``more_than`` and ``less_than`` arguments
which are both integers. This condition checks whether 
the scheduler has looped through the tasks for given
number of time. This is useful for testing to, for example,
do a short test that the scheduler launches your task.
It is extensively used in Rocketry's unit tests.

.. literalinclude:: /code/conds/api/scheduler_cycles.py
    :language: py
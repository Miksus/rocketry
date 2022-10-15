
Task Status
===========

Task status conditions are often useful for the end condition
to prevent running a task when an important task is running 
or for more advanced scheduling control.

Here is a list of task status conditions:

- ``rocketry.conds.started``: Task has started
- ``rocketry.conds.failed``: Task has failed
- ``rocketry.conds.succeeded``: Task has succeeded
- ``rocketry.conds.finished``: Task has finished

All of them support periods:

- ``this_minute``: Status happened in the current minute (fixed)
- ``this_hour``: Status happened in the current hour (fixed)
- ``this_day``: Status happened in the current day (fixed)
- ``today``: Alias for ``this_day``
- ``this_week``: Status happened in the current week (fixed)
- ``this_month``: Status happened in the current month (fixed)

All of the constrains supports additional constrains:

- ``before``: Status happened before given time
- ``after``: Status happened after given time
- ``between``: Status happened between given times
- ``on``: Status happened at given time


Here are examples:

.. literalinclude:: /code/conds/api/task_status.py
    :language: py

.. note::

    If the ``task`` is not given, the task is interpret to be
    the task the condition is set to.

Task Running
------------

There is also the condition ``rocketry.conds.running``. This 
condition is true if the given task (or the task itself if not
set) is running. There are also methods ``more_than``, ``less_than`` 
and ``between`` to specify timespan how long the task should be 
running for the condition to be true:

.. literalinclude:: /code/conds/api/task_running.py
    :language: py

This condition can also be used to set how many parallel runs
can happen (if multilaunch is set):

.. literalinclude:: /code/conds/api/task_running_multi.py
    :language: py
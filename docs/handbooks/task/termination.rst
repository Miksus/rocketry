
Termination
===========

Tasks can be terminated if any of the
following are met:

- Task has run longer than its timeout
- Task's ``end_cond`` is true
- Scheduler is immediately shutting down

.. warning::

    Only ``async``, ``thread`` and ``process`` tasks can be terminated. 
    Read more about the execution methods: 
    `execution method handbook <handbook-execution>`.

Timeout
-------

Timeout defines how long the task may run. It can be set on session level
and on task level. Task level timeout overrides the session setting so 
if a task does not have timeout specified the session setting is used 
instead.

To set it on task level:

.. code-block:: python

    @app.task(timeout="1 hour", execution="process")
    def do_things():
        ...

To set it on session level:

.. code-block:: python

    from rocketry import Rocketry

    app = Rocketry(config={"timeout": 0.1})

    @app.task(timeout="1 hour", execution="process")
    def do_things():
        ...

The timeout can be as:

- int or float (number of seconds)
- string (timedelta string)
- ``datetime.timedelta``

End Condition
-------------

End condition is a condition that when true, the task is terminated.
This is useful to prevent some tasks to run outside their intended 
period. For example, you may want to kill all running less important 
tasks when the actual production starts.

For example, this task will be terminated if it is running between
08:00 and 18:00 (8 am to 6 pm): 

.. code-block:: python

    from rocketry.conds import time_of_day

    @app.task(end_cond=time_of_day.between("08:00", "18:00"))
    def do_things():
        ...

Scheduler Shutdown
------------------

If scheduler shuts down with no errors (either shut_down was called or 
the scheduler shut condition was reached), the scheduler waits for the
running tasks to finish or to reach their timeout or end condition.

However, the scheduler will terminate all tasks during shutdown if:

- Scheduler encountered a fatal error
- The configuration :ref:`instant_shutdown <config_instant_shutdown>` is ``True``
- ``session.shut_down(force=True)`` was called
- ``session.shut_down()`` was called twice

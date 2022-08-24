
.. _cron:

Cron Scheduling
===============

Rocketry also natively supports `cron-like scheduling <https://en.wikipedia.org/wiki/Cron>`_.

Cron
----

Condition ``cron`` checks whether the current time is inside specified the cron 
interval and the task has not run in this interval. It is useful for running a task
the same way as cron would schedule it. 

You can specify the cron statement using string:

.. literalinclude:: /code/conds/api/cron.py
    :language: py

Or you can use named arguments:

.. literalinclude:: /code/conds/api/cron_kwargs.py
    :language: py

See more from the official documentation of cron or test using `crontab <https://crontab.guru/>`_.

.. note::

    Unlike most of the condition, the cron condition checks whether the task 
    has run on the period (as standard with cron schedulers) and not whether 
    the task has finished on the given period. 

Crontime
--------

Condition ``crontime`` is similar to ``cron`` but it is not tied to a task
and it only checks whether the current time is inside the specified cron interval.
It is useful if you want to augment the cron scheduling by adding retries or 
else.

.. literalinclude:: /code/conds/api/crontime.py
    :language: py

.. literalinclude:: /code/conds/api/crontime_kwargs.py
    :language: py

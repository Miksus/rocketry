
.. _cron:

Cron Scheduling
===============

Rocketry also natively supports `cron-like scheduling <https://en.wikipedia.org/wiki/Cron>`_.

You can input a cron statement as a string:

Examples
--------

.. literalinclude:: /code/conds/api/cron.py
    :language: py

Or you can use named arguments:

.. literalinclude:: /code/conds/api/cron_kwargs.py
    :language: py

See more from the official definition of cron.

.. note::

    Unlike most of the condition, the cron condition checks whether the task 
    has run on the period (as standard with cron schedulers) and not whether 
    the task has finished on the given period. 
.. _conditions-intro:

Conditions, Basics
==================

Conditions are vital part of Red Engine system
as they are responsible of determining when a 
task may start. They also can be used to determine
when the session will end or when a (parallelized) 
task should be killed. 

A condition can be either ``true`` or ``false``.
They can represent, for example, statement of 
current time (ie. it is afternoon now), a statement 
about a state (ie. the machine has internet access), 
presence of an event (ie. a task has successfully run) 
or presence of an thing (ie. a file exists).

There are two ways of creating conditions:

- Using Red Engine's string parser or
- Creating them from Red Engine's condition classes

The former is meant for being as human readable
and convenient as possible. Therefore this method 
is preferred and this section mostly covers that.

The conditions can be set to the tasks' initiation 
arguments directly as strings:

.. code-block:: python

    FuncTask(..., start_cond="daily between 10:00 and 14:00")

or you can set them to the ``start_cond`` of a task 
configuration file if that is preferred. To refresh how to 
set up tasks, see :ref:`creating-task`. The next examples 
can be directly supplied to the ``start_cond`` or to the 
``end_cond`` of a task.


Combining Conditions with Logic
-------------------------------

Conditions can also be combined using boolean logic. The 
conditions support the following operators: 

- ``&``: **AND** operator 
- ``|``: **OR** operator 
- ``~``: **NOT** operator

For example, ``<condition A> & <condition B>`` mean that the
statement is true only if both conditions (A and B) are true. 
Similarly ``<condition A> | <condition B>`` mean that either
A or B need to be true for the whole statement to be true and 
``~<condition A>`` mean that A must be false for the 
statement to be true. The operators can also be nested using 
parentheses.

In practice, this looks like:

.. code-block:: python

    FuncTask(..., start_cond="""
        (time of day between 08:00 and 10:00 & time of week between Monday and Friday) 
        | (time of day between 14:00 and 16:00 & ~time of week between Monday and Friday)
    """)

The starting condition of this task is ``True`` if the time is between 8 AM and 10 AM and 
current day is a week day or if the time is between 2 PM and 4 PM and current day is a non 
week day (weekend). There are more elegant ways to express the same but this is for the 
sake of example. Any condition can be combined with the same operators and next we will 
discuss about some useful conditions found from Red Engine.

.. _conditions-examples:

Conditions, Examples
====================

There are several categories of conditions:

- Time related conditions ('time of...'). These are conditions that are true or false depending
  on whether current time is within the period.
- Task related conditions. These are similar as time related conditions but these are also tied
  in the status of the task. Useful to set a task to run once in given period (ie. day).
- Scheduler related. These are conditions that check the state of the scheduler (ie. how many
  cycles of tasks it has run or how long ago it stated). Mostly useful for testing.
- Miscellaneous. Conditions can also check whether a parameter exists, whether a file exists,
  whether the machine has internet access, whether a row exists in a database etc. It is adviced
  to make your own condition classes when needed.

Next some examples from these categories are shown.

Time Related
------------

See :ref:`examples-cond-time` for list of actual examples.

- ``time of day between 10:00 and 14:00``

  - True if current time is between 10 AM and 2 PM.

- ``time of week between Monday and Wednesday``

  - True if current week day is Monday, Tuesday or Wednesday

- ``time of week on Monday``

  - True if currently is Monday.

- ``time of month after 5th``

  - True if if the current day of month is 5th or after.

.. warning::
    Be careful for not to use these as your only condition in the 
    ``start_cond``. The task will be rerun constantly during the 
    period.

Task Related
------------

See :ref:`examples-cond-task` for list of actual examples.

- ``every 10 minutes``

  - True if the task has not run in the past 10 minutes.
  - Useful for running the task once given time span.

- ``every 3d 2h 5min``

  - True if the task has not run in the past 3 days, 2 hours 
    and 5 minutes. See Pandas Timedelta for more.
  - Useful for running the task once given time span.

- ``daily``

  - True if the task has not run in current day.
  - Useful for running the task once a day.

- ``daily between 10:00 and 14:00``

  - True if the task has not run in current day between 10 AM 
    and 2 PM and current time is between 10 AM and 2 PM.
  - Useful for running the task once a day in given time.

- ``daily after 14:00``

  - True if the task has not run in current day after 2 PM and 
    current time is after 2 PM.
  - Useful for running the task once a day in given time.

- ``weekly between Monday and Wednesday``

  - True if the task has not run on Monday, Tuesday or Wednesday 
    and currently the week day is one of these.
  - Useful for running the task once a week in given week day(s).

You can also tie these with other tasks:

- ``task 'another task' has failed today``

  - True if task named "another task" failed today.

- ``task 'another task' has succeeded this hour``

  - True if task named "another task" succeeded in this hour.

- ``task 'another task' has terminated this week before Friday``

  - True if task named "another task" was terminated this week 
    before Friday.

- ``after task 'another task' succeeded``

  - True if the task this condition is set to (as `start_cond` or 
    `end_cond`) has not succeeded after task named 'another task'.
  - Useful to run the task straight after another task.

.. note::
    One can build task pipelines using these conditions (one task
    runs after another). However, you can also create pipelines with
    :py:class:`redengine.extensions.Sequence` which may be more convenient.


Scheduler Related
-----------------

- ``scheduler has more than 10 cycles``

  - True if the scheduler has run more than 10 cycles of tasks.

- ``scheduler has run over 10 minutes``

  - True if the scheduler started over 10 minutes ago.

Miscellaneous
-------------

- ``param 'x' exists``

  - True if session parameters have parameter `x`.

- ``param 'x' is 'myval'``

  - True if session parameters have parameter `x` and the value of the paramter is `myval`.
.. _handbook-cond-periodical:

Periodical Execution
====================

Time based scheduling is the base for most schedulers.
Often it is interpret that a task is set to run when 
a given time is reached and the task has not yet run
at that time, or given time has passed from the previous
run. Time based scheduling can be divided into two categories:

- Floating periods: Run when given time has passed from previous run
- Fixed period: Run at given time of day, week etc.

Floating Periods
----------------

Perhaps the simplest scheduling is to run a task
when a given amount of time has passed. This 
can be done by:

.. literalinclude:: /code/conds/api/every.py
    :language: py

.. note::

    The condition ``every`` is linked running the task
    

Fixed Periods
-------------

It is also common to have a task to run once in some 
agreed fixed time span. Such time spans are:

- hour: starts at 0 minute and ends at 60 minute
- day: starts at 00:00 and ends at 24:00
- week: starts on Monday at 00:00 and ends on Sunday at 24:00
- month: starts at 1st at 00:00 and ends 28rd-31st at 24:00

Running a task every hour is different than running a task
hourly in Rocketry. The difference is that the former runs
every time after 60 minutes has passed but the latter every
full hour. If time is now 07:15, the former will run at 
08:15 but the latter will run at 08:00.

.. literalinclude:: /code/conds/api/periodical.py
    :language: py


Constrained
^^^^^^^^^^^

The fixed periods can also be constrained using ``before``,
``after`` and ``between``:

- ``before``: From the beginning of the fixed period till the given time
- ``after``: From the given time to the end of the fixed period
- ``between``: From given start time to the given end time

So what this means in practice? Here is an illustration for a day/daily:

- *before 14:00*: From 00:00 (0 am) to 14:00 (2 pm)
- *after 14:00*: From 14:00 (2 pm) to 24:00 (12 pm)
- *between 08:00 and 16:00*: From 08:00 (8 am) to 16:00 (4 pm)

and some illustations what this means for a week/weekly:

- *before Friday*: From Monday 00:00 (0 am) to Friday 24:00 (12 pm)
- *after Friday*: From Friday 00:00 (0 am) to Sunday 24:00 (12 pm)
- *between Tuesday and Friday*: From Tuesday 00:00 (0 am) to Friday 24:00 (12 pm)

There are also *on/at* and *starting* methods:

- ``on/at``: On a given subunit of the period. The method ``on`` is an alias for ``at``.
- ``starting``: The fixed period starts on given time 

The subunit of a day is hour, the subunit of a week is day of week, subunit of a 
month is a day of month etc. To illustrate these options, 
*on Friday* means Friday 00:00 (0 am) to Tuesday 00:00,
*at 11:00 (daily)* means from 11:00 to 12:00
and *starting Friday* means the week is set to start on Friday.

.. literalinclude:: /code/conds/api/periodical_restricted.py
    :language: py

.. note::

    The logic follows natural language. Statement 
    ``between Monday and Friday`` means Monday at 00:00
    (0 am) to Friday 24:00 (12 pm).

There are also **time of ...** conditions check if the current time
is within the given period.


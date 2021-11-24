
Scheduling Guide
================

This tutorial covers common strategies to schedule
tasks to run on specific time. If you need to refresh how
to create tasks please see :ref:`short-guide` or :ref:`advanced-guide`
before reading further. This section also does not cover pipelining as 
that is covered in :ref:`pipeline-guide`.

You may also be interested in reading the :ref:`condition-syntax`.
To specify the interval when a task may run, it is easiest to 
use the :ref:`execution conditions <cond-execution>`. These 
conditions specify a period in which the task may start only 
once.


Once a day
----------

Perhaps the most common scheduling problem is to run a specific
function once a day. That is very simple to do:

.. code-block:: python

    @FuncTask(start_cond="daily")
    def do_daily():
        ... # Do once a day starting from 0 AM

You can also define the period when the task may run by:

.. code-block:: python

    @FuncTask(start_cond="daily between 08:00 and 10:00")
    def do_daily():
        ... # Do once a day starting between 8 AM and 10 AM 

You can extend the times the task runs using the *or* operator (``|``).
To run a task twice a day for example:

.. code-block:: python

    @FuncTask(start_cond="""daily between 08:00 and 10:00 
                          | daily between 14:00 and 15:00""")
    def do_daily():
        ... # Do twice a day first between 8 AM to 10 AM and then between 2 PM to 3 PM

You can also restrict the times the task runs using the *and* operator (``&``).
In such case it is advisable to use the :ref:`fixed interval <cond-fixedinterval>`.
To run once a day from Monday to Friday for example:

.. code-block:: python

    @FuncTask(start_cond="""daily & time of week between Monday and Friday""")
    def do_daily():
        ... # Do once a day on Mon, Tue, Wed, Thu and Fri

Once a week
-----------

Sometimes you may also run a task once (or more times) per week.
For this purpose, there is the *weekly* execution condition:

.. code-block:: python

    @FuncTask(start_cond="weekly")
    def do_weekly():
        ... # Do once a week starting from Monday

You may specify the day the task is allowed to run:

.. code-block:: python

    @FuncTask(start_cond="weekly on Tuesday")
    def do_weekly():
        ... # Do once a week on Tuesday

Or you may want to run it once in a weekend:

.. code-block:: python

    @FuncTask(start_cond="weekly between Sat and Sun")
    def do_weekly():
        ... # Do once a week between Saturday and Sunday

Or run it twice in a weekend:

.. code-block:: python

    @FuncTask(start_cond="weekly on Saturday | weekly on Sunday")
    def do_weekly():
        ... # Do twice a week on Saturday and Sunday

You can also constrain the task to run once a week and on specific time:

.. code-block:: python

    @FuncTask(start_cond="weekly & time of day between 10:00 and 14:00")
    def do_weekly():
        ... # Do once a week between 10 AM and 2 PM

More execution conditions
-------------------------

There is also *minutely*, *hourly* and *monthly* if the above examples were
insufficient. They work the same way and read from the 
:ref:`syntax specifications <cond-execution>` for more.
Note that fixed conditions such as *minutely* and *hourly* work on clock cycles 
and not always when, for example, 60 seconds or 60 minutes have passed. 
We cover scheduling for running a task after given time has passed next.

After given time passed 
-----------------------

You may want to run a task after given time has passed after the previous run 
of the task, for example 10 seconds. For that, there are the 
:ref:`time delta conditions <cond-timedelta>`. They use ``pandas.Timedelta``
which provides very flexible syntax.

To run once a minute passed from previous run:

.. code-block:: python

    @FuncTask(start_cond="every 1 minute")
    def do_after_given_period():
        ... # Do after given period

To run once an hour passed from previous run:

.. code-block:: python

    @FuncTask(start_cond="every 1 hour")
    def do_after_given_period():
        ... # Do after given period

To run once a day passed from previous run:

.. code-block:: python

    @FuncTask(start_cond="every 1 day")
    def do_after_given_period():
        ... # Do after given period

Or combine these:

.. code-block:: python

    @FuncTask(start_cond="every 1 day 10 hours 5 minutes 10 seconds")
    def do_after_given_period():
        ... # Do after given period

You can also set the task to run, for example, when 
one hour has passed but only between 10 AM and 5 PM
and on week days:

.. code-block:: python

    @FuncTask(start_cond="""every 1 hour 
                          & time of day between 10:00 and 17:00 
                          & time of week between Mon and Fri""")
    def do_after_given_period():
        ... # Do after given period


Complex examples
----------------

As you probably know, you can craft complex logics using the 
boolean operators (``&``, ``|`` and ``~``) or nesting 
conditions. In this section we introduce some more advanced
examples. 

Run hourly but if the task fails, don't today anymore:

.. code-block:: python

    @FuncTask(start_cond="every 1 hour & ~has failed today")
    def do_things():
        ... # Do whatever

Run twice a day but if fails, don't run the second time:

.. code-block:: python

    @FuncTask(start_cond="""(
            daily between 08:00 and 09:00 
            | daily between 15:00 and 17:00
        ) 
        & ~has failed today
    """)
    def do_things():
        ... # Do whatever

Run hourly but if the task fails, don't run for 7 days:

.. code-block:: python

    @FuncTask(start_cond="every 1 hour & ~has failed past 7 days")
    def do_things():
        ... # Do whatever
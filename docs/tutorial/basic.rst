.. _basic-tutorial:

Basic Tutorial
==============

This is a basic level tutorial.

Topics of the tutorial:

- Scheduling basics
- Execution options
- Changing log destination

Scheduling Basics
-----------------

Rocketry's scheduling system works with conditions
that are either true or false. A simple condition
could be *time is now between 8:00 (8 am) and 14:00 (2 pm)*.
If current time is inside this range, the condition
is true and if not, then it's false. If this is a condition 
for a task, it runs if the the current time is in this range. 

There are three ways of creating conditions:

- String syntax
- Condition API
- Condition classes

In this tutorial we will stick with the string syntax to keep
things simple. Read more about the options in :ref:`the handbook <condition-handbook>`.

There are a lot of scheduling options in Rocketry:
the tasks can run at specific time, after some other 
tasks have run or when other conditions are met. In 
this tutorial we focus on the time specific scheduling
as that is most used. In later tutorials we discuss 
other options.

Perhaps the simplest scheduling problem is to run a task
after a given time has passed. Here are some examples 
for such a scheduling:

.. literalinclude:: /code/conds/syntax/every.py
    :language: py

You may also schedule tasks to run on fixed time 
periods (ie. daily, weekly, monthly):

.. literalinclude:: /code/conds/syntax/periodical.py
    :language: py


But what if you wanted to schedule to run, for example,
daily but only in the afternoon? 
That's also easy:

.. literalinclude:: /code/conds/syntax/periodical_restricted.py
    :language: py

Notice how all of those support ``before``, ``after``, ``between``
and ``starting``. Running ``on`` something only makes sense on 
periods in which the time element is actually a time span, for 
example, Monday usually means Monday 00:00 to Monday 24:00 in 
natural language but 10 o'clock means exactly at 10:00.

Our previous examples were scheduled to run once in the
time periods we specified. There are also ``time of ...``
scheduling options for situations in which you wish 
to run the task constantly in the given period or 
if you wish to add them to other scheduling options 
(we get back to this later):

.. code-block:: python

    @app.task('time of day between 10:00 and 18:00')
    def do_constantly_during_day():
        ...

    @app.task('time of week between Saturday and Sunday')
    def do_constantly_during_weekend():
        ...

The handbook's :ref:`condition section <condition-handbook>`
has more examples if you wish to read more.

Execution Options
-----------------

There are three options for how tasks are executed:

- ``process``: Run the task in a separate process
- ``thread``: Run the task in a separate thread
- ``main``: Run the task in the main process and thread (default)

Here is a quick example of each:

.. literalinclude:: /code/execution.py
    :language: py

You may also put the default execution method
if there is one that you prefer in your project:

.. code-block:: python

    app = Rocketry(config={'task_execution': 'main'})

    @app.task("daily")
    def do_main():
        ...

There are pros and cons in each option. In short:

=========== =============  =====================  ========================
Execution   Parallerized?  Can be terminated?      Can modify the session?
=========== =============  =====================  ========================
``process`` Yes            Yes                    No
``thread``  Yes            Yes if task supports   Yes
``main``    No             No                     Yes
=========== =============  =====================  ========================


Changing Logging Destination
----------------------------

Logging the states of the tasks is vital for Rocketry's system.
This includes the logs about when each task started, succeeded 
and failed. This information is used in many of the scheduling 
statements and to prevent setting the same task running multiple
times.

Rocketry extends `logging library's <https://docs.python.org/3/library/logging.html>`_ 
loggers extending them with `Red Bird <https://red-bird.readthedocs.io/>`_
to enable reading the logs. 

By default, the logs are stored in-memory and they do not 
persist over if the scheduler is restarted. You may change 
the destination simply by creating a Red Bird repo and 
pass that as the ``logger_repo`` to the application.

**Storing the logs in-memory:**

.. code-block:: python

    from rocketry import Rocketry
    from redbird.repos import MemoryRepo

    app = Rocketry(
        logger_repo=MemoryRepo()
    )

**Storing the logs to CSV file:**

.. code-block:: python

    from rocketry import Rocketry
    from redbird.repos import CSVFileRepo

    app = Rocketry(
        logger_repo=CSVFileRepo(
            filename="logs.csv"
        )
    )

See more repos from `Red Bird documentation <https://red-bird.readthedocs.io/>`_.
We will get back on customizing the loggers in later tutorials.
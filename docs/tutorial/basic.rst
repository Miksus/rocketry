.. _basic-tutorial:

Basic Tutorial
==============

This is a basic level tutorial.

Topics of the tutorial:

- Basics of the application
- Basics of scheduling
- Basics of parallelization
- Basics of log data store

Application Basics
------------------

Rocketry's application instance is the highest level interface
to the scheduling system. You can set configurations,
create tasks, create custom conditions and start the scheduling session with it. 

Here is a simple example of how to create a minimal scheduler:

.. code-block:: python

    from rocketry import Rocketry
    from rocketry.conds import daily

    app = Rocketry()

    @app.task(daily)
    def do_things():
        ... # Put your code here

    if __name__ == "__main__":
        app.run()

What happened here:

- First we imported some components
- Then we created the Rocketry application
- Then we created a task that runs once a day
- Then we started the application in the main block

.. warning::

    It is recommended to always start Rocketry application
    in the block ``if __name__ == "__main__": ...`` as otherwise 
    you risk unintentionally starting the scheduler many times 
    if you use multiprocess parallelization. This block also ensures
    that the scheduler is not started if this Python file is simply 
    imported.

You can pass several configuration options to the application.
You can read more about those from :ref:`session configurations <config-handbook>`.

Scheduling Basics
-----------------

Rocketry's scheduling system works with logical conditions
which are either true or false. These statements can be 
practically anything and most often they are time-related.

Here is a simple illustration:

.. code-block:: python

    from rocketry.conds import true, false

    @app.task(true)
    def do_constantly():
        ...

    @app.task(false)
    def do_never():
        ...

The task ``do_constantly`` has ``true`` as its starting condition
meaning that it will start all the time. The task ``do_never`` has
``false`` in its starting condition and it will never start. 
In most cases you don't want your task to start all the time
(or never). We will get to more useful conditions later.

Because the starting conditions are just logical statements, we can 
also use logical operators (AND, OR, NOT) on them. Rocketry uses 
the bitwise operators for this purpose:

.. code-block:: python

    @app.task(true & true)
    def do_and():
        ...
    
    @app.task(true | false)
    def do_or():
        ...

    @app.task(~false)
    def do_not():
        ...

Here are the list of the operators:

- ``a & b``: a AND b
- ``a | b``: a OR b
- ``~a``: NOT a

You can also use parentheses to create 
complex combinations:

.. code-block:: python

    @app.task((true & true) | ~(false & true))
    def do_and():
        ...

There is a large collection of built-in conditions as well.
The conditions can be put into several categories:

- Time-based: run once an hour, when 10 seconds has passed etc.
- Task dependent: run after another task
- Custom: run based on purely custom logic
- A combination of above

Furthermore, the time-based conditions can be further divided to:

- Fixed time (ie. run once a day, a week, etc.)
- Floating time (ie. run when 10 seconds have passed)

and the time-based fixed time conditions can be divided to:

- Log dependent (whether a task has run in the given period)
- Stateless (whether the current time is in the given period)

Because there are so many options, we don't go through the options in
this tutorial. You can read more about them from 
:ref:`condition handbook <condition-handbook>`.

Here are some relevant sections to get started:

- :ref:`How to run a task periodically. <handbook-cond-periodical>`
- :ref:`How to run a task based on cron scheduling. <handbook-cond-cron>`
- :ref:`How to run a task after another. <handbook-cond-pipeline>`

Execution Options
-----------------

A Python function can be run in various ways: synchronously, 
asynchronously, threaded or in a subprocess. Rocketry's tasks 
can also be run using these options. Sometimes it makes sense
to run a task in a separate process and sometimes asynchronous
or threaded tasks are enough. You can pick the one that suits
each situation.

There is a summary of these options:

- ``process``: Run the task in a separate process
- ``thread``: Run the task in a separate thread
- ``async``: Run the task in async (default)
- ``main``: Run the task in the main process and thread

And here are quick examples of each:

.. literalinclude:: /code/execution.py
    :language: py

Typically ``thread`` or ``async`` are good options 
if your tasks are IO-bound. If your tasks are CPU-bound,
``process`` is often the best choice. If your tasks 
are short, then ``async`` is possibly the best. 
The option ``main`` is useful for maintenance tasks which 
should block running the other tasks.

You may also set the default execution method
if there is one that you prefer in your project:

.. code-block:: python

    app = Rocketry(execution="async")

    @app.task("daily")
    def do_main():
        ...

Read more about the execution types in :ref:`execution handbook <handbook-execution>`.


Changing Logging Destination
----------------------------

Storing the tasks' run history is cruicial for persistence of the scheduler.
If the scheduler is restarted it should know which task has already
run so that it won't rerun them needlessly. 

For this purpose, Rocketry has task loggers which store the information of when 
a task started, succeeded, failed or terminated. Rocketry uses 
`logging library's logging system <https://docs.python.org/3/library/logging.html>`_ 
for this. This is further extended using `Red Bird's <https://red-bird.readthedocs.io/>`_
`logging handlers <https://red-bird.readthedocs.io/en/stable/logging_handler.html>`_
to enable writing the logs to a data store which can be also read by Rocketry.

By default, the logs are stored in-memory and they will disappear 
if the scheduler is restarted. The data store for the task logs 
can be changed multiple ways:

- Via argument ``logger_repo``
- Using a setup hook (recommended)

The first one is demonstrated in this tutorial as it is simpler
and in the next tutorial we introduce the latter.

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

.. warning::

    As mentioned, ``MemoryRepo`` is non-presistent but it also accumulates memory
    unless manually cleared. Therefore it is suitable mostly for testing 
    and prototyping.

See more repos from `Red Bird documentation <https://red-bird.readthedocs.io/>`_.
We will get back on customizing the loggers in later tutorials.

.. _handbook-logging:

Task Logging
============

Rocketry's logging system is based on 
`logging library (standard library) <https://docs.python.org/3/library/logging.html>`_
and on `Red Bird <https://red-bird.readthedocs.io/>`_.
Rocketry uses Logging's logging mechanisms and extend
them with Red Bird in order to read from the logs.

Mechanism
---------

There is a logger called ``rocketry.task`` which is 
used to log the tasks' actions. This logger should 
have one repo handler (``redbird.logging.RepoHandler``)
which logs the task actions to a repository that 
can be read using Red Bird's unified query syntax. 
The logs, appart from failure, are logged with 
level ``INFO`` thus the logger should not filter
this level off.

Types of task actions:

- ``run``: Logged when a task starts.
- ``success``: Logged when a task finishes without exceptions.
- ``fail``: Logged when a task finishes with an error.
- ``terminate``: Logged when a task is terminated before it finished.
- ``inaction``: Special action to indicate the task did nothing. Requires raising a special exception.
- ``crash``: The task had previously silently crashed. This is to indicate that the task is no longer running.

Log Record
----------

Each log record in the repository should contain at 
least the following fields or attributes:

- ``created``: Timestamp when the log record was created (Logging library creates).
- ``task_name``: Name of the task.
- ``action``: What the log was about. Either *run*, *success*, *fail*, *terminate* or *inaction*. 

You may add any other field or attribute from what the Logging 
library creates or create attributes your own.

Here is a minimal example of a log record model that Red Bird 
accepts:

.. code-block:: python

    from pydantic import BaseModel

    class MinimalRecord(BaseModel):
        task_name: str
        action: str
        created: float

Log record models are passed to the repo handlers to specify the data
format in which our logs are. We take a look into this in a bit.

Here are some premade log record models you may use:

- ``rocketry.log.MinimalRecord``: Bare minimum for the logging to work.
- ``rocketry.log.LogRecord``: Has the typical elements of `logging.LogRecord <https://docs.python.org/3/library/logging.html#logging.LogRecord>`_ and extras required by rocketry.
- ``rocketry.log.MinimalRecord``: Has the same as ``LogRecord`` but also includes start, end and runtimes.


Setting Up Repo to a Logger
---------------------------

By default, Rocketry creates a repo handler with ``MemoryRepo``
in it. This handler logs the records only to an in-memory Python
list that is not maintained when the interpreter is closed.

You may want to log the records to disk in order to maintain
persistence in scheduler's state in case of restart or shutdown. 

First, we fetch the task logger:

.. code-block:: python

    import logging
    logger = logging.getLogger('rocketry.task')

Here is an example to log to a CSV file:

.. code-block:: python

    from rocketry.log import MinimalRecord

    from redbird.repos import CSVFileRepo
    from redbird.logging import RepoHandler

    # Creating the repo
    repo = CSVFileRepo(filename="path/to/repo.csv", model=MinimalRecord)

    # Adding the repo to the logger
    logger = logging.getLogger('rocketry.task')
    handler = RepoHandler(repo=repo)
    logger.addHander(handler)

Another common pattern is to log the records to a 
SQL database. This can be done with SQLAlchemy:

.. code-block:: python

    from redbird.repos import SQLRepo
    from sqlalchemy import create_engine

    engine = create_engine("sqlite:///app.db")
    repo = SQLRepo(engine=engine, table="tasks", if_missing="create", model=MinimalRecord, id_field="created")
    
    handler = RepoHandler(repo=repo)
    logger.addHander(handler)

Read more about repositories from `Red Bird's documentation <https://red-bird.readthedocs.io/>`_.

Querying the Logger
-------------------

Here is an illustration of getting the repository:

.. code-block:: python

    import logging
    logger = logging.getLogger('rocketry.task')
    for handler in logger.handlers:
        if hasattr(handler, "repo"):
            break

    repo = handler.repo

Then we can query this repo:

.. code-block:: python

    repo.filter_by(task_name="my_task", action="run").all()

The ``task_name`` is already injected if you
call the logger in a task. Tasks use a ``TaskAdapter``
that does this trick:

.. code-block:: python

    @app.task()
    def do_things():
        ...

    task_logger = app.session['do_things'].logger
    task_logger.filter_by(action="run").all()

Read more about querying from `Red Bird's documentation <https://red-bird.readthedocs.io/>`_.

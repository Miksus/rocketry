.. _intermediate-tutorial:

Intermediate Tutorial
=====================

This is an intermediate level tutorial.
In this tutorial we go through aspects
that you might not come across in very
simple applications but you eventually
need to know.

Running as Async
----------------

By default, ``app.run`` starts a new event loop. 
If you wish to integrate other async apps, such 
as FastAPI, you can also call ``app.serve`` method
which is an async method to start the scheduler:

.. literalinclude:: /code/demos/minimal_async.py
    :language: py

Session Configurations
----------------------

There are several options to tune the scheduling session.
You might want to change some of the default configurations
depending on your project. You might want to silence more 
errors on production than by default and you might want 
to change the default execution type.

Read more from the :ref:`the config handbook <config-handbook>`.

Using the Condition API
-----------------------

Previously we have used only the string syntax for scheduling.
For simple use cases that is sufficient but if your project 
grows the strings may become a burden. The code analyzers cannot
identify possible typos or other problems in them and there is a 
limitation in reuse. To fix these, there is a condition API that
provides functions and instances that are quite similar than the
components in the string syntax.

Here are some examples of how the condition API looks like:

.. literalinclude:: /code/conds/api/simple.py
    :language: py

Read more about the condition API in :ref:`the handbook <condition-api>`.
From now on, we swith to the condition API but you are free to use the 
string syntax. Most things work very similarly in both.

Condition Logic
----------------

Previously we have introduced some ways to schedule tasks.
Sometimes the existing options are not enough and you need
to compose a scheduling logic from multiple conditions. 
For such purpose, there are logical operations:

- ``&``: *AND* operator 
- ``|``: *OR* operator 
- ``~``: *NOT* operator

Using these are pretty simple:

.. literalinclude:: /code/conds/api/logic.py
    :language: py

We used conditions ``true`` and ``false`` but you 
may replace these with other conditions (ie. ``daily``) 
from previous examples. Also note how we can use parentheses

.. note::

    The operations are the same with string syntax. 
    This is valid condition syntax: 
    
    ``"(true & false) | (false & ~true)"``


Pipelining
----------

Rocketry supports two types of task pipelining:

- Run a task after another has succeeded, failed or both
- Put the return or output value of a task as an input argument to another

Run Task After Another
^^^^^^^^^^^^^^^^^^^^^^

There is are conditions that can be used for this purpose:

.. literalinclude:: /code/conds/api/pipe_single.py
    :language: py

Set Output as an Input
^^^^^^^^^^^^^^^^^^^^^^

To pipeline the output-input, there is an *argument*
for the problem. We go through arguments and parametrization
with more detail soon but here is an example to pipeline
the task returns:

.. literalinclude:: /code/params/return.py
    :language: py

Of course, the second task is not quaranteed to run after 
the first. You can combine the both to achieve proper
pipelining:

.. literalinclude:: /code/conds/api/pipe_with_return.py
    :language: py


Parameterizing
--------------

Parameters are key-value pairs passed to the tasks.
The value of the pair is called *argument*. The 
argument can be derived from the return of another 
task, from the return value of a function or 
a component of the scheduling framework.

There are also two scopes of parameters: session level
and task level. Most of the time you are using session 
level parameters.

Here is an illustration of using a session level parameter:

.. code-block:: python

    from rocketry.args import Arg

    # Setting parameters to the session
    app.params(
        my_arg='Hello world'
    )

    @app.task()
    def do_things(item = Arg('my_arg')):
        ...

We set a session level parameter (``my_arg``)
and we used that in the task ``do_things``.
When the task is run, function argument ``item``
will get the value of ``my_arg`` from session
level arguments which is ``"Hello world"``.
This argument can be reused in multiple tasks
as it was set on session level. 

Setting an argument to task level only looks like 
this:

.. code-block:: python

    from rocketry.args import SimpleArg

    @app.task()
    def do_things(item = SimpleArg('Hello world')):
        ...

``SimpleArg`` is just a placeholder argument that 
is simply the value that was passed (which is 
``'Hello world'``). In the example above the argument
is not reusable in other tasks.

Next we will cover some basic argument types that 
have more functionalities.

Function Argments
^^^^^^^^^^^^^^^^^

Function arguments are arguments which values are 
derived from the return value of a function. To 
set a session level function argument:

.. code-block:: python

    from rocketry.args import Arg

    @app.param('my_arg')
    def get_item():
        return 'hello world'

    @app.task()
    def do_things(item = Arg('my_arg')):
        ...


To set task-level-only function argument:

.. code-block:: python

    from rocketry.args import FuncArg

    def get_item():
        return 'hello world'

    @app.task()
    def do_things(item = FuncArg(get_item)):
        ...


Meta Argments
^^^^^^^^^^^^^

Meta arguments are arguments that contain 
a component of the scheduling system.
These are useful when you need to manipulate
the session in a task (ie. shut down the 
scheduler or add/delete tasks) or manipulate
some tasks (ie. force running or change 
attributes).

An example of the session argument:

.. code-block:: python

    from rocketry.args import Session

    @app.task()
    def manipulate_session(session = Session()):
        ...

An example of the task argument:

.. code-block:: python

    from rocketry.args import Task

    @app.task()
    def manipulate_task(this_task=Task(), another_task=Task('do_things')):
        ...

This is more advanced and we will get to the usage of these later.

Task Logging
------------

Rocketry uses `Red Bird's <https://red-bird.readthedocs.io/>`_
`logging handler <https://red-bird.readthedocs.io/en/latest/logging_handler.html>`_
for implementing a logger that can be read programmatically.
Red Bird is a repository pattern library that abstracts 
database access from application code. This is helpful 
to create a unified interface to read the logs regardless
if they are stored to a CSV file, SQL database or to 
a plain Python list in memory.

Log to Repository
^^^^^^^^^^^^^^^^^

By default, the logs are put to a Python list and they are gone
if the scheduler is restarted. In many cases this is undesired
as the scheduler does not know which task had already run,
succeeded or failed in case of restart. Therefore you might want
to store the log records to a disk by changing the default log 
repository. 

The simplest way to configure the location of the logs is to
pass the new repo as ``logger_repo``:

.. code-block:: python

    from rocketry import Rocketry
    from rocketry.log import MinimalRecord
    from redbird.repos import CSVFileRepo

    repo = CSVFileRepo(filename="tasks.csv", model=MinimalRecord)
    app = Rocketry(logger_repo=repo)

In the example above, we changed the log records to go to a CSV file
called *tasks.csv*. We also specified a log record format that contains
the bare minimum. Read more about logging :ref:`in the logging handbook <handbook-logging>`.

Add Another Log Handlers
^^^^^^^^^^^^^^^^^^^^^^^^

As the logger is simply extension of `the logging library <https://docs.python.org/3/library/logging.html>`_,
you can also add other logging handlers as well: 

.. code-block:: python

    import logging
    from rocketry import Rocketry

    app = Rocketry()

    # Create a handler
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)

    # Add the handler
    task_logger = logging.getLogger('rocketry.task')
    task_logger.addHandler(handler)

.. warning::

    Make sure the logger ``rocketry.task`` has at least 
    one ``redbird.logging.RepoHandler`` in handlers or 
    the system cannot read the log information.

Task Naming
-----------

Each task should have a unique name within
the session. If a name is not given to a task,
the name is derived from the arguments of the
task.

For function tasks if the name is not specified,
the name is set as the name of the function:

.. code-block:: python

    >>> @app.task()
    >>> def do_things():
    >>>     ...

    >>> app.session[do_things].name
    'do_things'

.. warning::

    As the name must be unique, an error is raised if you try
    to create multiple tasks from the same function or from 
    multiple functions with same names without specifying name.

You can pass the name yourself as well:

.. literalinclude:: /code/naming.py
    :language: py

.. note::

    If you use the decotator (``@app.task()``) to define function
    task, the decorator returns the function itself due to pickling
    issues on some platforms. However, the task can be fetched from
    session using just the function: ``session[do_things]``.
    There is a special attribute (``__rocketry__``) in 
    the task function for enabling this.

.. note::

    Task names are used in many conditions and in logging.
    They are essential in order to find out when a task 
    started, failed or succeeded. 

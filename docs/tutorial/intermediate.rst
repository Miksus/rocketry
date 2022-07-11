.. _intermediate-tutorial:

Intermediate Tutorial
=====================

This is an intermediate level tutorial.
In this tutorial we go through aspects
that you might not come across in very
simple applications but you eventually
need to know.


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

Customizing Logging Handlers
----------------------------

Rocketry uses `Red Bird's <https://red-bird.readthedocs.io/>`_
`logging handler <https://red-bird.readthedocs.io/en/latest/logging_handler.html>`_
for implementing a logger that can be read programmatically.
Red Bird is a repository pattern library that abstracts 
database access from application code. This is helpful 
to create a unified interface to read the logs regardless
if they are stored to a CSV file, SQL database or to 
a plain Python list in memory.

As the logger is simply extension of `the logging library <https://docs.python.org/3/library/logging.html>`_,
you may add other logging handlers as well: 

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

Reading from the Logs
---------------------

Reading programmatically from the logs is easy due to unified 
querying syntax of Red Bird.

Simply 

.. code-block:: python

    import logging
    
    task_logger = logging.getLogger('rocketry.task')

    # Getting a RepoHandler
    for handler in task_logger.handlers:
        if hasattr(handler, "repo"):
            break
    
    # Query all logs from the handler
    handler.filter_by().all()

Read more about the querying from `Red Bird's documentation <https://red-bird.readthedocs.io/en/latest/>`_
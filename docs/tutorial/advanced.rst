.. _advanced-tutorial:

Advanced Tutorial
=================

This is an advanced level tutorial. In this tutorial
we introduce some concepts that are useful for more
advanced use cases.

Running as Async
----------------

By default, ``app.run`` starts a new event loop. 
If you wish to integrate other async apps, such 
as FastAPI, you can also call ``app.serve`` method
which is an async method to start the scheduler:

.. literalinclude:: /code/demos/minimal_async.py
    :language: py

Task Types
----------

So far, we have only used ``FuncTask`` with passing a callable.
There are other task types as well to cover most common use cases:

- ``FuncTask``: Executes a Python function
- ``CommandTask``: Executes a shell command

Here are the ways to initialize tasks:

.. code-block:: python

    @app.task('daily')
    def do_things():
        ...

    def run_things():
        ...
    
    app.task('daily', func=run_things)

    app.task('daily', func_name="main", path="path/to/example.py")

    app.task('daily', command='echo "Hello world"')


Metatasks
---------

The scheduler system can be modified in runtime.
You could during the runtime:

- shut down the scheduler
- restart the scheduler
- force a task to be run
- disable a task
- create, update or delete tasks

To do there, you can create a task that
runs either as a separate thread or on 
the main loop and pass the session or a
task in the task parameters. Tasks parallelized as 
separate processes cannot alter the 
scheduling environment due to limitations 
with sharing memory. 

To access the session:

.. code-block:: python

    from rocketry.args import Session

    @app.task(execution="thread")
    def do_shutdown(session=Session()):
        session.shutdown()

You can also access other tasks in runtime.
To do so, use ``Session`` or ``Task`` 
arguments to access tasks. 

We have the following task:

.. code-block:: python

    @app.task()
    def do_things():
        ... # Just some task

To access this task using the ``Session`` argument:

.. code-block:: python

    from rocketry.args import Session

    @app.task(execution="thread")
    def read_task(session=Session()):
        # Get by name
        task = session['do_things']

        # Or by function
        task = session[do_things]
        ...

        # Or just loop the tasks
        for task in session.tasks:
            if task.name == "do_things":
                break
        ...

To access this task using the ``Task`` argument:

.. code-block:: python

    from rocketry.args import Task

    @app.task(execution="thread")
    def read_task(task=Task(do_things)):
        ...

Access Task Logs
----------------

Now that we know how to access tasks in runtime,
we can read the logs of our task.

Let's take this again as an example:

.. code-block:: python

    @app.task()
    def do_things():
        ...

Then we make a task that fetch the task and queries
its log:

.. code-block:: python

    from rocketry.args import Session

    @app.task(execution="thread")
    def read_logs(session=Session()):
        task = session['do_things']

        run_logs = task.logger.filter_by(action="run").all()
        success_logs = task.logger.filter_by(action="success").all()
        fail_logs = task.logger.filter_by(action="fail").all()
        ...

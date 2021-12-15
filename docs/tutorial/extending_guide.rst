.. _extending-guide:

Extending Guide
===============

There are plenty of features prebuilt to Red Engine but there might come a 
situation that you need a custom condition, a custom task class or run 
specific code when each task fails. In this section we discuss how to 
extend Red Engine to more specific needs.

Custom Condition
----------------

In previous guides we already discussed how you can schedule your tasks using
``start_cond`` or terminate them with ``end_cond`` (if 
parallelized). There may be a situation in which there is 
no suitable condition for your purpose. For such case you 
can create your own condition easily using either ``FuncCond`` or ``TaskCond``.
If the condition is quick to check you can go with ``FuncCond``. If the 
condition may take time or may get stuck you can use ``TaskCond``

Here is a summary of the condition types:

==================  ======================  =============================
Property            FuncCond                TaskCond
==================  ======================  =============================
**Function runs**   when condition checked  in the background
**Useful for**      Simple/fast checks      I/O bound or expensive checks
==================  ======================  =============================


Function Condition
^^^^^^^^^^^^^^^^^^

You can create your own conditions and add them 
to the Red Engine condition parsing using ``FuncCond``.
Let's create some custom conditions to 
``project/models/conditions.py``:

.. code-block:: python

    import re
    import os
    from redengine.conditions import FuncCond

    @FuncCond(syntax="has work")
    def has_work():
        # Should return True or False
        return True

    @FuncCond(syntax=re.compile(r"folder (?P<folder>.+) has files")
    def has_files(folder):
        "Checks whether folder has content"
        return bool(os.listdir('/your/path'))

Now you can use these conditions simply by:

.. code-block:: python

    @FuncTask(start_cond="has work")
    def do_work():
        ... # Code to do your work

    @FuncTask(start_cond="folder C:/Temp has files")
    def process_files():
        ... # Code to process the files

As observed, to use ``has_work`` condition you just need
to include ``has work`` in your condition strings. The 
condition ``has_files`` is slightly more complex: you 
need to pass a string that matches to the regex pattern
``folder (?P<folder>.+) has files``. The value of the 
named regex group ``folder`` is passed as a keyword 
argument to the function ``has_files``.

Task Condition
^^^^^^^^^^^^^^

``TaskCond`` allows you to make a condition which state
is checked using a separate task. This is very useful 
for conditions which are I/O bound, may get stuck or 
take excess resources. ``TaskCond`` is simply a 
condition which state is determined by the output value
of a ``FuncTask`` that runs in the background.

.. code-block:: python

    import re
    import os
    from redengine.conditions import TaskCond

    @TaskCond(syntax=re.compile("data exists for (?P<date>.+)"), start_cond="every 10 minutes")
    def has_data():
        ... # Expensive code
        return True

Now you can use this condition simply:

.. code-block:: python

    @FuncTask(start_cond="data exists for today")
    def process_data():
        ... # Code to process data

The condition ``has_data`` will create a task called ``_condition-...has_data`` that
runs in the background every 10 minutes and returns the state of the condition. Between the runs the 
task value is whatever was the outcome of the latest run. If the task has not previously
run the state of the condition is ``False``. There is also a ``cooldown`` argument to 
``TaskCond`` which determines the time when the latest run of the task is considered
too old to count as the state and the state of the task is reverted back to ``False``
till the task runs again.

The task can have any settings that any ``FuncTask`` has: you can specify the ``execution``,
``end_cond``, ``priority``, ``timeout`` etc.

Custom Task
-----------

For most use cases ``FuncTask`` is probably sufficient
but in some cases it makes sense to create a new task 
class. Such situation may arise when you need to run 
code in different language and would like to have 
better abstraction for it.

For example, let's create a task to run SQL code:

.. code-block:: python

    from redengime.core import Task

    class SQLTask(Task):
        """A task that executes specified string 
        of SQL with given SQLAlchemy engine"""

        engine = create_engine('sqlite://')

        def __init__(self, query, *args, **kwargs):
            self.query = query
            super().__init__(*args, **kwargs)

        def execute(self, **kwargs):
            # The actual method executed when the task runs
            with engine.connect() as con:
                return con.execute(self.query, **kwargs)

        def get_default_name(self):
            # Name of a task if the name is not specified
            return self.query

Now we can use this task:

.. code-block:: python

    SQLTask(
        "DELETE FROM mytable WHERE mycol = :myval",
        start_cond="daily after 23:00",
        parameters={"myval": "my value"}
    )

Note that the same is achievable with ``FuncTask`` fairly
easily but if you have multiple such tasks that executes
SQL, this is more readable solution. 

If you need more customization, you can specify methods:

- ``.prefilter_params(params)``: Filtering parameters before creating a thread/process, or when getting the paramters.
- ``.postfilter_params(params)`` Fiiltering parameters after creating a thread/process, or right before the ``execute``.
- ``.process_failure(exc_type, exc_val, exc_tb)``: Runned when the task fails.
- ``.process_success(output)``: Runned when the task succeeds.
- ``.process_finish(status)``: Runned when the task finished, regardless of how.
- ``.get_default_name()``: Get a name for the task when a name was not specified.

See more in :class:`redengine.core.Task`.

Hooks
-----

You can add your own logic in between of Red Engine's
execution flow using hooks. They are simply functions 
or generators that are executed in specific parts of Red 
Engine's code. Hooks are stored in the session object 
and therefore if you recreate it the previous hooks 
will be removed.

Example use cases for hooks include:

- Disable production tasks not to run in testing 
- Send notification when the scheduler has started and shut down
- Send notification when any task has failed

Task Hooks
^^^^^^^^^^

Task init hook is useful for controlling the initiation 
of all tasks. An example of the hook:

.. code-block:: python

    from redengine.core import Task

    @Task.hook_init
    def my_init_hook(task):
        # Run before Task.__init__
        ...
        yield
        # Run after Task.__init__
        ...

Task execution hook is useful for injecting code 
to starting and finishing the execution of all tasks.
An example of such hook:

.. code-block:: python

    @Task.hook_execute
    def my_execution_hook(task):
        # Run before executing the task
        ...
        exc_type, exc, tb = yield
        # Run after the task has executed
        ...

A tuple of the exception type, the exception and 
the traceback object are sent to the generator.
Note that this hook runs in the child thread, if
``execution='thread'``), or process, if 
``execution='process'``.

.. warning::

    The hooks must be picklable meaning that you
    should not use, for example, lambda functions.

Scheduler Hooks
^^^^^^^^^^^^^^^

There are also several hooks you can use to 
control what happens on each part of the 
scheduler. Some examples of these hooks:

.. code-block:: python

    from redengine.core import Scheduler

    @Scheduler.hook_startup
    def my_startup_hook(scheduler):
        # Run before starting up scheduler
        ...
        yield
        # Run after the scheduler has started up
        ...

    @Scheduler.hook_cycle
    def my_cycle_hook(scheduler):
        # Run before running a cycle of tasks
        ...
        yield
        # Run after running a cycle of tasks
        ...

    @Scheduler.hook_shutdown
    def my_shutdown_hook(scheduler):
        # Run before starting shutdown
        ...
        yield
        # Run after finishing shutdown
        ...
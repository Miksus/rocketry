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
can create your own condition easily.

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
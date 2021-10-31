.. _cust-task:

Custom Task
===========

Custom task classes can be made by subclassing 
:class:`redengine.core.Task`.

Here is a practical demonstration:

.. code-block:: python

    from redengime.core import Task

    class SQLTask(Task):
        """A task that executes specified string 
        of SQL with given SQLAlchemy engine"""

        def __init__(self, *args, query, engine, **kwargs):
            super().__init__(*args, **kwargs)
            self.query
            self.engine = engine

        def execute(self, **kwargs):
            with engine.connect() as con:
                return con.execute(self.query, **kwargs)

Now we can use this task:

.. code-block:: python

    from redengine.tasks import FuncTask
    from sqlalchemy import create_engine

    SQLTask(
        query="DELETE FROM mytable WHERE mycol = :myval",
        engine=create_engine('sqlite://'),
        start_cond="daily after 23:00",
        parameters={"myval": "my value"}
    )

When this task executes, it will run the delete statement
and deletes all records where mycol is `my value`. 

Of course similar outcome could be achieved with
``FuncTask``. However, subclassing ``Task`` is a 
valid option when you need to separate the initiation
and execution or you need custom parameter handling.

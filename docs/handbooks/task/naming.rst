.. _handbook-task-naming:

Task Naming
===========

Each task should have a unique name within
the session. If a name is not given to a task,
the name depends on the task type and it may be 
derived from the initiation arguments of the task.

For function tasks the name is derived from the 
name of the function if not specified:

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

    If you use the decorator (``@app.task()``) to define function
    task, the decorator returns the function itself due to pickling
    issues on some platforms. However, the task can be fetched from
    session using just the function: ``session[do_things]``.
    There is a special attribute (``__rocketry__``) in 
    the task function for enabling this.

.. note::

    Task names are used in many conditions and in logging.
    They are essential in order to find out when a task 
    started, failed or succeeded. Because of this, it is 
    not advised to rename a task later unless the logs
    are cleared as well.
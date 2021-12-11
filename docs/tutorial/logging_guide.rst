.. _logging-guide:

Logging Guide
=============

Logging is a vital part of the Red Engine's system. The information of what 
tasks have run, when and with what status are relevant in order to determine 
many of the conditions in the system. Red Engine simply leverages 
`logging library <https://docs.python.org/3/library/logging.html>`_
that is part of Python's standard library. In this section we discuss how 
you can customize the task logger and the details around it.

How it works
------------

The most important logger in Red Engine's ecosystem is ``redengine.task``. This logger is 
used to log when a task ran, succeeded, failed, terminated or inacted. Furthermore,
Red Engine must be able to also read these records in order to determine whether a task 
have run already, if a task have succeeded etc. and for this purpose this logger should 
have at least one handler that can also be read or queried for the log records. This readable 
handler, called two-way handler, must have either a method  ``.read()`` and or ``.query(filtering)``
and methods should return an iterable of dictionaries about the log records, for example a list 
of dictionaries.

First we discuss about practical matters of how to add own handlers, like logging to terminal, 
to the logger and then how the two-way logger works and how to create your own.

Adding a handler
----------------

You can freely add your own handlers to the task logger if you wish to show the 
logging information about the tasks to terminal, in a file, send via email or so.
For example, displaying the execution in terminal:

.. code-block:: python

    import logging

    # Get the task logger
    logger = logging.getLogger("redengine.task")
    
    # Create handler and formatter
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    
    # Add to the logger
    logger.addHandler(handler)

.. _logging-schemes:

Schemes and prebuilt handlers
-----------------------------

As mentioned, you also need one handler capable for reading. You can set this 
either manually or use a premade scheme in creating a session. Currently 
there are the following options for such purpose:

===============================  ===========  ===========================================
Handler                          Scheme       Description
===============================  ===========  ===========================================
**redengine.log.MemoryHandler**  log_memory   Stores the log records to an in-memory list
**redengine.log.CsvHandler**     log_csv      Stores the log records to a CSV file
===============================  ===========  ===========================================



Schemes are premade configurations that can be initiated with a session.
Example of how to use a scheme:

.. code-block:: python

    from redengine import Session

    # Log and read the records to and from memory
    Session(scheme=["log_memory"])


To set a handler manually:

.. code-block:: python

    import logging
    from redengine.log import MemoryHandler, CsvHandler, CsvFormatter

    logger = logging.getLogger("redengine.task")

    # Use in-memory handler
    handler = MemoryHandler()
    logger.addHandler(handler)

    # Or use CSV handler
    formatter = CsvFormatter(fields=[
        task_name,
        asctime,
        action,
        start, # Start time of the task
        end, # End time of the task ('run' does not have end)
        runtime,
        message
    ])
    handler = CsvHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)


.. warning::

    In addition to the two-way logger, there are some other 
    small details you should be aware when modifying the logger.
    Here is a checklist the logger ``redengine.task`` should have:

    - have the log level set to ``INFO`` or ``DEBUG``,
    - have no filters
    - have at least one handler which has:
        
        - either ``.read`` or ``.query`` method or both
        - no filters

    It is also inadvisable to use the task logger outside of Red Engine. 


Custom two-way Handler
----------------------

You can also create your own two-way handler if you wish to log the records to a different 
storage, like SQL. To do so, you can just subclass the ``logging.Handler`` like you would 
typically subclass handlers. Just remember to add either ``.read`` or ``.query`` methods, 
or both. In addition to the regular ``LogRecord`` attributes, the following extras are also set as
attributes to the logged records which can be utilized:

- ``task_name``: Name of the task the log record is about
- ``action``: Action of the task of which the log record is about (success, fail etc.)
- ``start``: Start time of the task as datetime
- ``end``: End time of the task as datetime, not passed if action is ``run``
- ``runtime``: Time it took to run the task as timedelta, not passed if action is ``run``

Both, ``read`` and ``query`` methods, should return an iterable of dictionaries (ie. a list of dict)
and the dictionaries should contain at least the following keys:

- ``task_name``: Name of the task the log record is about
- ``timestamp``, ``created`` or ``asctime``: Time when the log record occurred.
- ``action``: Action of the task of which the log record is about (success, fail etc.)

.. note::

    There is a ``RecordFormatter`` that determines when the log recod occurred from the output of the ``read`` or
    ``query`` methods. If ``timestamp`` is found, it is parsed and used as such. If ``created`` is found, it is 
    parsed to datetime from epoch. If ``asctime`` is found, that is used and parsed to datetime.

The method ``.read`` should require no arguments and just return
all the log records. The necessary filtering is done after calling the method. 
However, the method ``.query`` should also take the query as an argument. 
The query is an object that represents a logical lazy evaluated expression. 

For example if you implement the ``query`` method, this call:

.. code-block:: python

    from redengine.pybox import query
    qry = query.parser.from_kwargs(
        task_name="a task", 
        timestamp=(datetime.datetime(2021, 1, 1), datetime.datetime(2021, 1, 2)),
        action=["fail", "success", "terminate"]
    )
    handler.query(qry)

should return log records where the ``task_name`` is *a task*, and where the ``timestamp``
is between *2021-01-01* and *2021-01-02* (including the start and end), and where
the action is either *fail*, *success* or *terminate*.

.. note::

    As it may be slow to query constantly the log records, there is some optional optimization. 
    If ``session.config['force_status_from_logs']`` is false, the task related conditions query or
    read the task logger's handlers only if the cached task attributes ``last_run``, ``last_success``,
    ``last_fail``, ``last_terminate`` or ``last_inaction``  are insufficient to determine 
    the state.
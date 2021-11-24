.. _session-info:

Session
=======

:class:`redengine.Session` is a container of the Red Engine ecosystem.
They contain the configurations, scheduled tasks, 
shared parameters and the scheduler itself.
All of these should exist prefetably in one session.
It is so important that Red Engine has always one made
for you by default:

.. code-block:: python

    from redengine import session

For convenience, Red Engine is aggressive on setting 
the created objects to sessions. Even tasks that 
did not specify such are set to the default session. 

If you wish to create your own session and set all 
the newly created Red Engine objects to this session,
you can simply do:

.. code-block:: python

    from redengine import Session
    mysession = Session(...)

See :py:class:`redengine.Session` for parameters 
to a session.

Examples of how to set up the session:

- :ref:`Standalone <standalone-session>`
- :ref:`Minimal <minimal-session>`
- :ref:`Simple <simple-session>`

Configurations
--------------

The session configurations are options that tune the behaviour of 
the system error handling and system flow. These can be passed as dict
in ``config`` argument of a :class:`redengine.Session`. There are following
configuration options:

- ``task_pre_exist``: What to do when creating a task which name already exists. Options:

    - ``raise``: Raise an error
    - ``replace``: Remove the previous task and add the new task to the session
    - ``ignore``: Don't set the new task to the session and leave the previous
    - ``rename``: Add number(s) to the name of the new task until it has unique name

- ``use_instance_naming``: If name not specified, use ``id(task)`` as the name of the task
- ``silence_task_prerun``: Don't crash the scheduler if a task fails outside the actual execution. Task is always logged as fail.
- ``silence_cond_check``: Don't crash the scheduler if checking a condition fails. If False, the state of a crashed condition is considered ``False``.
- ``force_status_from_logs``: Force the task related conditions always read the logs to determine the state. If false, the cached state is used if possible for optimization.
- ``cycle_sleep``: Seconds to wait after executing each cycle of tasks. By default no wait. 
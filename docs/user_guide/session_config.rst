Configuring the session
=======================

Sessions are containers of the Red Engine ecosystem.
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
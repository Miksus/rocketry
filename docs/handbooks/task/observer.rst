Observer Task
=============

Observer tasks are tasks that are running constantly
on the side. Observer tasks can be used for:

- Monitoring the system
- Hosting user interface or polling user inputs
- Polling events or updates

Observer tasks are characterized as tasks that
are not expected to complete and don't have 
timeouts. Unlike other tasks, observer tasks are 
always immediately terminated when shutting down
the scheduler regardless of the shutdown settings.

To set a task as an observer task, set ``permanent``
as ``True``:

.. code-block:: python

    @app.task(permanent=True)
    def monitor():
        while True:
            ...

.. note::

    If you use threaded execution for observer task,
    you should periodically check the termination flag 
    status:

    .. code-block:: python

        from rocketry.args import TerminationFlag
        from rocketry.exc import TaskTerminationException

        @app.task(permanent=True)
        def monitor(flag=TerminationFlag()):
            while not flag.is_set():
                ...
            raise TaskTerminationException()
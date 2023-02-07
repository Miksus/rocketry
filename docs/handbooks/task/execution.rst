
.. _handbook-execution:

Execution
=========

There are four methods to execute Rocketry tasks:

- ``main``: Run on synchronously in main thread and process
- ``async``: Run asynchronously
- ``thread``: Run on separate thread
- ``process``: Run on separate process

Example usage:

.. literalinclude:: /code/execution.py
    :language: py

Here is a summary of the methods:

=========== =============  =====================  ========================
Execution   Parallelized?  Can be terminated?      Can modify the session?
=========== =============  =====================  ========================
``process`` Yes            Yes                    No
``thread``  Partially      Yes if task supports   Yes
``async``   Partially      Yes if awaits          Yes
``main``    No             No                     Yes
=========== =============  =====================  ========================

If your problem is CPU bound (uses a lot of computational resources), you 
should use ``process`` as the execution type. If your problem 
is IO bound, then you should use ``async`` if your IO libraries support async and 
``thread`` if they don't support. If you wish to run your code completely 
synchronously, use ``main``.

Note that ``process`` cannot share the memory with the scheduler engine thus
it cannot modify its content on runtime. Therefore if you wish to build APIs 
or other ways modify the scheduler on runtime you should use either ``main``,
``async`` or ``thread`` as the execution type.

``main`` and ``async`` are the least expensive in terms of time and resources it
takes to initiate such task. ``thread`` has some overhead and ``process`` has 
quite significantly.

You can also set the default execution method that is used if task does not specify
it:

.. code-block:: python

    app = Rocketry(execution="async")

    @app.task()
    def do_main():
        ...


Main
----

This execution method runs the task unparallelized on main thread and 
process. The executed task can utilize async but tasks with
this execution type blocks the scheduler to do anything else
when such a task is running. In other words, if a task with 
this execution type is running, the scheduler cannot check
and launch other tasks in the mean time or do anything else.

.. note::

    If the task can utilize async but the scheduler will not continue 
    scheduling until the task is completed (failed or success). 

    For example, this task blocks the scheduler:

    .. code-block:: python

        @app.task(execution="main")
        async def do_async():
            ...

.. warning::

    Tasks with execution ``main`` cannot be terminated. If they get stuck,
    the scheduler will get stuck.

Useful if you wish to run synchronously and block all other execution
in the scheduler in the meantime.


Async
-----

This execution method runs the task asynchronously using `asyncio library <https://docs.python.org/3/library/asyncio.html>`_. 
The task should utilize the async in order to gain benefits over
``main`` execution method. Otherwise the task will block scheduler
to do other things such as launching other tasks, terminating tasks
or checking shutting conditions. 

.. code-block:: python

    import asyncio

    @app.task(execution="async")
    async def do_sync():
        await asyncio.sleep(10) # Do something async

.. warning::

    Your task also should also use async. Otherwise the task 
    may completely block the scheduler and the end result is the same 
    as running with execution as ``main``. The task also cannot be 
    terminated if it does not ``await``.

    This does not benefit from async:

    .. code-block:: python

        @app.task(execution="async")
        def do_sync():
            ...

    And neither does this (as it does not use ``async.sleep``):

    .. code-block:: python

        import time

        @app.task(execution="async")
        asnyc def do_sync():
            time.sleep(10) # Do something without await

.. warning::

    If a task with execution ``async`` gets stuck and it cannot call ``await``,
    the scheduler will get stuck as well.

.. note::

    Due to `GIL (Global Interpreter Lock) <https://wiki.python.org/moin/GlobalInterpreterLock>`_, 
    only one Python line can be executed at once. 
    Therefore pure Python code without any IO operations won't have 
    any performance benefits. However, if there are IO operations, there could 
    be improvements in performance.

In order to make ``async`` task to be terminated, the task should await at some point.

Useful for IO bound problems or to integrate APIs.


Thread
------

This execution method runs the task on a separate thread using 
`threading library <https://docs.python.org/3/library/threading.html>`_. 

.. note::

    Due to `GIL (Global Interpreter Lock) <https://wiki.python.org/moin/GlobalInterpreterLock>`_, 
    only one Python line can be executed at once. 
    Therefore pure Python code without any IO operations won't have 
    any performance benefits. However, if there are IO operations, there could 
    be improvements in performance.

In order to make ``thread`` task to be terminated, the task should listen the termination flag:

.. code-block:: python

    from rocketry.args import TerminationFlag
    from rocketry.exc import TaskTerminationException

    @app.task(execution="thread")
    def do_thread(flag=TerminationFlag()):
        while True:
            ... # Do something
            if flag.is_set():
                raise TaskTerminationException()

.. warning::

    If a task with execution ``thread`` never finishes and it does not respect termination, 
    the scheduler cannot shut down itself. 

.. note::

    Terminated thread tasks should raise ``TaskTerminationException`` to signal
    they finished prematurely due to termination. Without an exception, the task
    was considered to run successfully.

Useful for IO bound problems where there are no async support.


Process
-------

This execution method runs the task on a separate process using 
`multiprocessing library <https://docs.python.org/3/library/multiprocessing.html>`_. 

.. warning::

    The process cannot share memory with the main scheduler thus you cannot 
    modify the state of the scheduler from tasks parallelized with ``process``.
    However, you may still pass parameters to the task.

.. warning::

    You cannot pass parameters that cannot be pickled to tasks with
    ``process`` as the execution type. 

.. warning::

    Especially using ``process`` execution type, running the application **must be**
    wrapped with ``if __name__ == "__main__":`` block or otherwise launching a process
    task may launch another instance of the scheduler. Also, you should not wrap the 
    task function with decorators with execution type as ``process`` as otherwise 
    serialization of the function fails in initiating the process.

Useful for CPU bound problems or for problems in which the code has tendency to get stuck.

Multilaunch
-----------

By default, each task can be set running only once. In other words, if a task is 
already running it cannot be started even if its starting condition was still true
or it was set running using ``task.run()``. This limitation is in place to make 
sure the task logs are consistent. 

To illustrate this, your task must finish before it could be started again:

======= ========= =======
created task_name action
======= ========= =======
1       do_things run
2       do_things success
3       do_things run
4       do_things success
======= ========= =======


However, in some cases is not preferable and you might want to allow same task to 
start multiple times. This can be done by setting ``multilaunch`` true either on session 
configuration or to an individual task:

.. code-block:: python

    app = Rocketry(config={'multilaunch': True})

    @app.task(multilaunch=True)
    def do_things():
        ...

This task can produce logs similar to the following:

======= ========= =======
created task_name action
======= ========= =======
1       do_things run
2       do_things run
3       do_things success
4       do_things success
======= ========= =======

There is also a ``run_id`` passed to logs which you can 
use to identify individual runs and track their finish.

.. code-block:: python

    from rocketry.log import MinimalRunRecord

    app = Rocketry(config={'multilaunch': True})

    # Setting the log record model
    repo = app.session.get_repo()
    repo.model = MinimalRunRecord

    @app.task(multilaunch=True)
    def do_things():
        ...

By default, this will produce log similar to this:

======= ========= ========= =======
created task_name run_id    action
======= ========= ========= =======
1       do_things fe5018... run
2       do_things fab4db... run
3       do_things fe5018... success
4       do_things fab4db... success
======= ========= ========= =======

By default, ``run_id`` is a Universal Unique Identifier (UUID).
You can also create custom run IDs based on, for example,
the arguments:

.. code-block:: python

    import json
    def generate_run_id(task, params=None):
        return json.dumps(dict(params), default=str)
    
    @app.task(multilaunch=True, func_run_id=generate_run_id)
    def do_things(report_date):
        ...

You can also set the generator function as the session default:

.. code-block:: python

    app = Rocketry(config={'multilaunch': True, 'func_run_id': generate_run_id})

When the task is run (with a date parameter), the logs could look like:

======= ========= ============================= =======
created task_name run_id                        action
======= ========= ============================= =======
1       do_things {"report_date": "2022-01-01"} run
2       do_things {"report_date": "2022-01-02"} run
3       do_things {"report_date": "2022-01-01"} success
4       do_things {"report_date": "2022-01-02"} success
======= ========= ============================= =======

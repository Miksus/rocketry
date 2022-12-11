.. _cookbook-control-runtime:

Controlling Runtime
===================

There are several cases where one may want 
to control the runtime scheduling session:

- Create maintenance tasks.
- Command the scheduler from a user interface.
- Command the scheduler from an external program.

The interaction with the scheduling session is 
meant to be done via the ``session`` instance. This 
can be accessed using argument ``rocketry.args.Session``:

.. code-block:: python

    from rocketry.args import Session

    @app.task()
    def do_things(session=Session()):
        ...

Alternatively, you can access this by simply using the ``app.session``.
However, for bigger applications it is advised to use the argument.

Manipulating the Session
------------------------

To restart the scheduler in a task:

.. code-block:: python

    from rocketry.args import Session

    @app.task()
    def restart(session=Session()):
        session.restart()

To shut down the scheduler in a task:

.. code-block:: python

    from rocketry.args import Session

    @app.task()
    def shut_down(session=Session()):
        session.shut_down()

Manipulating Other Tasks
------------------------

To remove a task from the scheduler:

.. code-block:: python

    from rocketry.args import Session

    @app.task()
    def do_things():
        ...

    @app.task()
    def remove_task(session=Session()):
        session.remove_task("do_things")

To create a task:

.. code-block:: python

    from rocketry.conds import daily
    from rocketry.args import Session

    def do_things():
        ...

    @app.task()
    def remove_task(session=Session()):
        session.create_task(func=do_things, start_cond=daily)

Accessing a Task
----------------

You can also access other tasks in runtime. This is useful
for inspecting attributes of another task including its
status and logs. You can also set a task running using
the task instance.

You can use the ``Task`` argument:

.. code-block:: python

    from rocketry.args import Task

    @app.task()
    def do_on_self(this_task=Task()):
        ...

    @app.task()
    def do_on_other(another_task=Task(do_on_self)):
        ...

Or you can use the session:

.. code-block:: python

    from rocketry.args import Session

    @app.task()
    def do_things(session=Session()):
        task = session["do_things"]
        ...

Task Queue
----------

Task queue is a list of tasks that are run one after another.
Rocketry also supports run specific parameters thus you can
also create a parametrized task queue.

Here is an example:

.. code-block:: python

    from rocketry.args import Session
    import asyncio

    def next_task():
        "Get next task from the queue"
        yield 'do_things', {}
        yield 'do_report', {'report_date': '2022-01-01'}

    @app.task(on_startup=True, execution="async")
    async def task_queue(session=Session()):
        queue = next_task()
        for task_name, params in queue:            
            task = app.session[task_name]
            task.run(**params)
            
            # Wait till finish
            while task.is_running:
                await asyncio.sleep(5)


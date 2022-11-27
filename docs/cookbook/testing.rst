Testing
=======

This section covers how to test some parts of 
Rocketry's system including the conditions and
the scheduler.

Conditions
----------

The conditions have method ``observe`` that is 
used by the system to evaluate the state (whether
the condition is true or false). 

Here is a simple example:

.. code-block:: python

    from rocketry.conds import true, false

    cond = true | false
    
    assert cond.observe()

However, some conditions also require the task 
or the session to determine their state. Conditions
that don't require them still accepts them.

.. code-block:: python

    from rocketry.conds import daily

    @app.task()
    def do_things():
        ...

    assert daily.observe(task=do_things, session=app.session)

Tasks
-----

You can run a specific once task using the scheduler. This can 
be done with ``session.run``:

.. code-block:: python

    from rocketry import Rocketry

    app = Rocketry()

    @app.task()
    def do_things():
        ...

    if __name__ == "__main__":
        app.session.run(do_things)

Scheduler
---------

Sometimes you might want to test the full system in a unit test.
However, unlike often with production, you don't want your unit tests
to run indefinitely. To prevent this, you can set a shutdown condition
to the scheduler.

This scheduler runs 5 minutes before automatically ending itself:

.. code-block:: python

    from rocketry import Rocketry
    from rocketry.conds import scheduler_running

    app = Rocketry(shut_cond=scheduler_running(more_than="5 minutes"))

    @app.task()
    def do_things():
        ...

    if __name__ == "__main__":
        app.run()

After this, you can test the task logs or other items.

Setting Custom Time
-------------------

You can also test scheduling and task triggering by forcing 
Rocketry to use custom time.

For example, if you wish to fix scheduling to start at 
12:00 on 12th of May 2014:

.. code-block:: python

    import datetime
    import time

    from rocketry import Rocketry
    from rocketry.conds import daily

    def fix_time(dt):
        "Get new time measurement function"
        start_time = time.time()
        def get_time():
            sec_since_start = time.time() - start_time
            return dt.timestamp() + sec_since_start
        return get_time

    app = Rocketry(config={"time_func": fix_time(datetime.datetime(2014, 5, 31, 12, 00))})

    @app.task(daily)
    def do_things():
        ...

    if __name__ == "__main__":
        app.run()

.. note::

    We used nested functions to reuse fixing the time. If it looks
    confusing, you can also use a flat function with globals:

    .. code-block:: python

        START_TIME = time.time()
        DATETIME = datetime.datetime(2014, 5, 31, 12, 00)
        def get_time():
            sec_since_start = time.time() - START_TIME
            return DATETIME.timestamp() + sec_since_start

        app = Rocketry(time_func=get_time)
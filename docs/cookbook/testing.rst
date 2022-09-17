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
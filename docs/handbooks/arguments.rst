.. _handbook-arguments:

Arguments
=========

Arguments are dynamic values for parameter key-value pairs. 
Read first about parameters from :ref:`handbook-parametrization`.

There are several argument types:

- ``SimpleArg``: dummy argument, useful only for testing
- ``FuncArg``: the value is the return of a given function
- ``Arg``: session argument
- ``Task``: a task instance
- ``Session``: the session instance

The value of the arguments inspected only when needed, ie. when 
executing a task. This process of inspecting the argument values 
is called argument *materialization*.

.. note::

    If you don't use an argument instance as the value of a parameter
    pair, the passed value will be whatever you put.


Pipelining
----------

Arguments can also be pipelined. This is useful if you have multiple 
sources for a parameter and would like to get the one that is available.

.. code-block:: python

    from rocketry.args import Arg, EnvArg, CliArg

    env_arg = EnvArg('ROCKETRY_ENV') >> CliArg('--env') >> Arg('env') >> SimpleArg('test')

    @app.task()
    def do_things(arg=env_arg):
        ...

The above will take the value of the environment ``ROCKETRY_ENV`` if this exists,
else it will take the CLI argument ``--env`` if this exists, else it will take
the session argument ``env`` if this exists and if none of the previous exists 
it will take the value ``test``. 

SimpleArg
---------

``SimpleArg`` is an argument that simply is the given value.
It is useful mostly in testing.

.. code-block:: python

    from rocketry.args import SimpleArg

    @app.task()
    def do_things(arg=SimpleArg('a value')):
        ...

Arg
---

``Arg`` is an argument that simply is the given value.
It is useful mostly in testing.

.. code-block:: python

    from rocketry.args import Arg

    @app.task()
    def do_things(arg=Arg('my_session_param')):
        ...

    app.params(my_session_param="a value")

.. note::

    You can also pass ``default`` which is used
    if the session parameter is not found: ``Arg('myparam', default="a value")``

FuncArg
-------

``FuncArg`` is an argument that will have the value
of a given function when the argument is materialized.

.. code-block:: python

    from rocketry.args import FuncArg

    def get_value():
        return 'a value'

    @app.task()
    def do_things(arg=FuncArg(get_value)):
        ...

EnvArg
------

``EnvArg`` is an argument that will have the value
of a given environment variable.

.. code-block:: python

    import os
    from rocketry.args import EnvArg

    @app.task()
    def do_things(arg=EnvArg("MY_ARG")):
        ...

    os.environ['MY_ARG'] = 'a value'

.. note::

    You can also pass ``default`` which is used
    if the environment variable is not found: ``EnvArg('MY_ARG', default="a value")``

CliArg
------

``CliArg`` is an argument that will have the value
of a given CLI argument.

.. code-block:: python

    from rocketry.args import CliArg

    @app.task()
    def do_things(arg=CliArg("--myparam")):
        ...

Then call the program:

.. code-block:: console

    python myscript.py --myparam "a value"

.. note::

    You can also pass ``default`` which is used
    if the CLI argument is not found: ``CliArg('--myparam', default="a value")``

Return
------

``Return`` is an argument that will have the return value
of another task. It is useful for pipelining tasks' outputs.

.. code-block:: python

    from rocketry.args import Return

    @app.task()
    def do_first():
        ...
        return 'a value'

    @app.task()
    def do_second(arg=Return(do_first)):
        ...

.. note::

    You can also pass ``default`` which is used
    if the return value is not found: ``Return('mytask', default="a value")``

Task
----

``Task`` is an argument that will have the task instance
as the value when materialized. It is useful for advanced
metatasks that manipulate other tasks.

.. code-block:: python

    from rocketry.args import Task

    @app.task()
    def do_things(arg=Task()):
        ...

Alternatively, you can specify another task to use:

.. code-block:: python

    from rocketry.args import Task

    @app.task()
    def do_other():
        ...

    @app.task()
    def do_things(arg=Task(do_other)):
        ...

TerminationFlag
---------------

``TerminationFlag`` is an argument that will have a 
``threading.Event`` as the value. The event will be set
when the task is set to be terminated. It is useful 
for creating a threaded tasks that obey termination
process.


.. code-block:: python

    from rocketry.args import TerminationFlag

    @app.task()
    def do_second(arg=TerminationFlag()):
        while not flag.is_set():
            ... # Do things

.. note::

    The task should raise ``rocketry.exc.TaskTerminationException``
    if the flag was set as otherwise the task is considered to be 
    successful (instead of terminated).

Session
-------

``Session`` is an argument that will have the session instance
as the value when materialized. It is useful for advanced
metatasks that manipulates on the session, ie. for runtime APIs
or other external communication with the scheduler.

.. code-block:: python

    from rocketry.args import Session

    @app.task()
    def do_things(arg=Session()):
        ...
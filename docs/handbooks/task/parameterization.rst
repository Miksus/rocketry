
Parameterization
================

Parameters can be set on task level or on session level
where they can be used by multiple tasks or conditions.

Here are short definitions of the relevant terms:

.. glossary::

    parameter
        Key-value pair that can be passed to a task
        to utilize.

    argument
        Value of the key-value pair or parameter.

Here is an example to initiate a session level parameter:

.. code-block:: python

    @app.params(my_arg="Hello world")

This sets a parameter called ``"my_arg"`` to the session.
When this parameter is used, the function will be executed
and the return value will be used as the paramter value.

Here is an example to use it in a task:

.. code-block:: python

    from rocketry.args import Arg

    @app.task()
    def do_things(arg=Arg("my_arg")):
        assert arg == "Hello world"
        ...

Here is an example to use it in a custom condition:

.. code-block:: python

    from rocketry.args import Arg

    @app.cond("is foo")
    def is_foo(arg=Arg("my_arg")):
        assert arg == "Hello world"
        ...
        return True

You can also use this argument in another argument:

.. code-block:: python

    @app.param("my_arg_2")
    def get_my_arg(arg=Arg("my_arg")):
        assert arg == "Hello world"
        return "Hello world 2"

.. warning::

    The arguments may end up in infinite recursion if 
    argument *x* requests argument *y* and argument 
    *y* requests argument *x*.


Arg
---

The value of ``rocketry.args.Arg`` is acquired from the
session level parameters. The value is whatever is stored
behind a given key in the session parameters.

A simple example:

.. code-block:: python

    from rocketry.args import Arg

    app.params(my_arg="Hello")

    @app.task()
    def do_things(arg=Arg("my_arg")):
        ...
        return "Hello world"

The argument in session parameters can be plain Python object
or another argument such as ``FuncArg``

You can access the parameters using ``app.session.parameters``.


Return
------

Argument ``rocketry.args.Return`` represents a return 
value of a task. It can be used to pipeline input-output
of tasks.

.. code-block:: python

    from rocketry.args import Return

    @app.task()
    def do_things():
        ...
        return "Hello world"

    @app.task()
    def do_things(arg=Return(do_things)):
        ...
        return "Hello world"

Alternatively, you can also refer to the task name using string:

.. code-block:: python

    from rocketry.args import Return

    @app.task()
    def do_things():
        ...
        return "Hello world"

    @app.task()
    def do_things(arg=Return("do_things")):
        ...
        return "Hello world"

FuncArg
-------

Function argument (``rocketry.args.FuncArg``) is an argument
which value represents the return value of a function. The 
function is run every time the argument value is evaluated.

A simple example:

.. code-block:: python

    from rocketry.args import FuncArg

    def get_my_arg():
        ...
        return "Hello world"

    @app.task()
    def do_things(arg=FuncArg(get_my_arg)):
        ...
        return "Hello world"


You can also set the ``FuncArg`` to the session parameters
using a wrapper in the application and pass the ``FuncArg``
using ``Arg`` to a task:

.. code-block:: python

    from rocketry.args import Arg

    @app.param("my_arg")
    def get_my_arg():
        ...
        return "Hello world"

    @app.task()
    def do_things(arg=Arg("my_arg")):
        ...

Alternatively, you can use the function:

.. code-block:: python

    from rocketry.args import Arg

    @app.param("my_arg")
    def get_my_arg():
        ...
        return "Hello world"

    @app.task()
    def do_things(arg=Arg(get_my_arg)):
        ...

Special Arguments
-----------------

There are also arguments which represents
a component in Rocketry's ecosystem.

Here is a list of those:

.. glossary::

    ``rocketry.args.Task``
        The value is a task instance. 

        Example:

        .. code-block:: python

            from rocketry.args import Task

            @app.task()
            def do_things(task=Task()):
                if task.last_success:
                    ...

    ``rocketry.args.Session``
        The value is the session instance. 

        Example:

        .. code-block:: python

            from rocketry.args import Session

            @app.task()
            def do_things(session=Session()):
                session.shut_down()

    ``rocketry.args.TerminationFlag``
        The value is a threading event to indicate when
        the task has been called to be terminated. Should
        be used tasks with execution as ``thread`` and those
        tasks should check the value of this flag periodically
        (``.is_set()``) and raise ``rocketry.exc.TaskTerminationException``
        if the flag is set. Otherwise, the threaded task cannot 
        be terminated.

        Example:

        .. code-block:: python

            from rocketry.args import TerminationFlag
            from rocketry.exc import TaskTerminationException

            @app.task(execution="thread")
            def do_things(flag=TerminationFlag()):
                while True:
                    if flag.is_set():
                        raise TaskTerminationException()
                    ...


.. _handbook-parametrization:

Parameterization
================

Parameters are key-value pairs that are passed to the tasks.
The value of a pair can be any instance or an *argument* which
is a dynamic value. Read more about arguments in :ref:`handbook-arguments`.

There are several levels of parameters:

1. **Batch parameters**: set to individual runs
2. **Task parameters**: specified to a task
3. **Function parameters**: specified to a task function
4. **Session parameters**: specified to the session

The parameters override themselves in the above order,
**batch parameters** override **task parameters** and 
**task parameters** override **function parameters**.
Only parameters with the same keys are overridden and 
the execution of a task can utilize all of the parameter
levels. 

Batch Parameters
----------------

Batch parameters are parameters set to an individual 
run. They are stored in ``batches`` attribute in tasks.
Each run of a task consumes the oldest batch parameters.
If there are none, no batch parameters are used.

Batch parameters are useful when you want to run tasks
manually with other parameters than they normally run 
with.

Here is an example:

.. code-block:: python

    @app.task()
    def do_things(arg):
        ...

    # Getting a task instance
    task = app.session[do_things]

    # Setting batch run
    task.run(arg="a value")

.. note::

    The above only sets the task running once when the 
    scheduling session starts. Typically you want to
    set it running depending on custom logic when the 
    scheduler is already running, ie. when a user 
    requests to run a task. To do so, you can create
    a metatask that gets the tasks that should be 
    run manually and then set them running with 
    correct parameters
    
    .. code-block:: python

        from rocketry.conds import minutely

        @app.task()
        def do_things(arg):
            ...

        def get_task_to_run():
            ... # Get name of the task to run
            return {
                'name': 'do_things', 
                'params': {'arg': 'a value'}
            }

        @app.task(minutely, execution="main")
        def manual_run():

            # Get the task to run and its parameters
            task_to_run = get_task_to_run()
            task_name = task_to_run['name']
            params = task_to_run['params']

            # Set the task running with the given
            # parameters
            task = app.session[task_name]
            task.run(params)

Task Parameters
---------------

Task parameters are specified in the task initiation.

To set task parameters:

.. code-block:: python

    @app.task(parameters={"arg": "a value"})
    def do_things(arg):
        ...

Function Parameters
-------------------

Function parameters are parameters in the function's
signature.

To set function parameters:

.. code-block:: python

    from rocketry.args import SimpleArg

    @app.task()
    def do_things(arg=SimpleArg('a value')):
        ...

.. note::

    The above example is simple but not practical.
    There are other dynamic argument types that 
    are more practical such as ``Arg`` which 
    takes value from the session parameters.

Session Parameters
------------------

Session parameters are set to the session level.
They are used if nothing else were set.

To set session parameters:

.. code-block:: python

    from rocketry.args import SimpleArg

    app.params(arg=SimpleArg('a value'))

Alternatively:

.. code-block:: python

    @app.param("arg")
    def get_arg():
        return 'a value'

Parameters in Conditions and Parameters
---------------------------------------

Parameters can also be accessed in custom conditions 
and other parameters.

To use in custom condtion:

.. code-block:: python

    from rocketry.args import Arg

    @app.cond("is foo")
    def is_foo(arg=Arg("my_arg")):
        assert arg == "Hello world"
        ...
        return True

To use in custom parameter pairs:

.. code-block:: python

    @app.param("my_arg_2")
    def get_my_arg(arg=Arg("my_arg")):
        assert arg == "Hello world"
        return "Hello world 2"

.. warning::

    The arguments may end up in infinite recursion if 
    argument ``A`` requests argument ``B`` and argument 
    ``B`` requests argument ``A``.

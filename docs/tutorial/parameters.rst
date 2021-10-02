
.. _parametrizing:

Parametrizing Tasks
===================

There are also many ways to pass additional 
data to the tasks. One can put the data to 
a file that is read during the task's
execution (ie. in the user defined function) 
or the data can be passed as parameters.
In this section, we focus on the latter.

There are two layers of parameters in Red
Engine:

- Task parameters: These are task specific and not shared.
- Session parameters: These are available to all tasks.

In case there are two parameters with the same name, the 
the task specific parameter is preferred over the session 
level parameter.

Task Level Parameters
---------------------

The task level parameters are simple to make: just add 
them to the initiation of the task:

.. code-block:: python

    from redengine.tasks import FuncTask
    @FuncTask(parameters={"x": "foo", "y": "bar"})
    def my_task(x, y):
        ...

The parameters should always be dictionaries (keyword arguments).
Positional arguments are not (yet) supported.

Session Level Parameters
------------------------

As stated, session parameters are accessible by all tasks.
The task class should filter the parameters from the 
session that the task requires to run. This logic can 
be altered by creating custom parameter filtering to task 
classes or by creating custom argument classes. We go to 
arguments in a moment.

The session level arguments can be set in multiple ways,
for example:


- Setting manually to a session object, like:

.. code-block:: python

    from redengine import session
    session.parameters["my_param"] = "a value"

- Setting to the ``parameters: ...`` in a session configuration
  file, like:

.. code-block:: yaml

    ...
    parameters:
        my_param: 'a value'
    ...

- Setting via ``Argument`` classes, like:

.. code-block:: python

    from redengine.arguments import Arg
    Arg.to_session(my_param="a value")

The first two methods are fairly obvious but the third is 
interesting. Most ``Argument`` classes have method ``to_session`` that 
acts as a convenient constructor for special types of parameters.
A bit more till we get to the arguments.

As discussed, tasks use the session parameters as according
to their own filtering rules. Some tasks might not use session 
parameters (or even task level parameters) at all but generally 
they use the parameters that are as arguments in the method 
``.execute(...)`` of the task class.

For example, this task will automatically use the parameter
we set as session level parameter:

.. code-block:: python

    from redengine.tasks import FuncTask

    @FuncTask(name="mytask")
    def myfunc(my_param):
        ...

Arguments
---------

Arguments represent simply the value of a parameter key-value 
pair. However, how the value is actually determined can be 
anything. For example, the parameter value can depend on the 
the task it is being put to, some external resources 
or the state of the scheduler. The same argument object can 
be shared by multiple tasks allowing changing the argument 
at one go. Arguments prove some interesting strategies to 
parametrize tasks.

For example, the argument ``FuncArg`` provide some interesting
ways to define dynamic parameters. 

.. code-block:: python

    from redengine.arguments import FuncArg

    FuncArg.to_session("my_param")
    def some_stuff():
        ...
        return 'a value'

When this is executed, there will be a parameter ``my_param``
in the session parameters. When a task requests this parameter,
the ``some_stuff`` function is executed and the value of the 
parameter is the return value. This is somewhat similar as Pytest's
fixtures.

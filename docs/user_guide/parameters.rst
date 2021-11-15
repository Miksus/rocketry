
.. _parametrizing:

Parametrizing Tasks
===================

There are many ways to pass additional 
data to the tasks. One can put the data to 
a file and read it during the task's
execution or pass the data as parameters.
In this section, we focus on the latter method.

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

What happens here is that when the task is executed 
the argument ``x`` will receive value *foo* and the 
argument ``y`` will receive value *bar*. The parameters 
should always be dictionaries (keyword arguments).
Positional arguments are not (currently) supported.

.. note::

  Task level parameters are never filtered and always 
  passed to the task execution. 

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

- Setting via ``Argument`` classes, like:

.. code-block:: python

    from redengine.arguments import Arg
    Arg.to_session(my_param="a value")

The first method is fairly obvious but the second is 
interesting. Most ``Argument`` classes have method ``to_session`` that 
acts as a convenient constructor for special types of parameters.
A bit more till we get to the arguments.

If you would like to set more dynamic session parameters, you 
can use ``FuncParam`` that is used similarly as ``FuncTask``
or ``FuncCond``:

.. code-block:: python

    from redengine.parameters import FuncParam

    @FuncParam()
    def my_param():
        return 'a value'

Optinally, you can pass ``name='my_param'`` to the ``FuncParam``
if you would like to name the parameter as different than the 
function name.

As discussed, tasks use the session parameters as according
to tasks' own filtering rules. Some tasks might not use session 
parameters (or even task level parameters)´. The default behaviour
is that task use the session parameters that are specified as the 
named arguments in the method ``.execute(...)`` of the class type.
This can be overridden when creating custom task classes.

For example, this task will automatically use the parameter
we set as session level parameter called ``my_param``:

.. code-block:: python

    from redengine.tasks import FuncTask

    @FuncTask(name="mytask")
    def myfunc(my_param):
        ...

Arguments
---------

Arguments represent simply the value of a parameter key-value 
pair, parameters themselves. How the value is actually determined can be 
anything. For example, the parameter value can depend on the 
the task it is being put to, some external resources 
or the state of the scheduler. The same argument object can 
be shared by multiple tasks allowing changing the argument 
at one go. Arguments prove some interesting strategies to 
parametrize tasks.

For example, the argument ``FuncArg`` provide similar way
of setting dynamic parameters as ``FuncParam``: 

.. code-block:: python

    from redengine.arguments import FuncArg

    FuncArg.to_session("my_param")
    def some_stuff():
        ...
        return 'a value'

This is essentially the same as using ``FuncParam``. However, ``FuncParam``
is preferred due to being syntactically closer of how ``FuncTask`` and
``FuncCond`` look creating more uniform code.

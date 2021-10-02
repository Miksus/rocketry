
 
Creating Tasks
==============

The whole purpose of this framework is to schedule 
tasks or jobs. There are various types of tasks and 
endless ways to create new ones and therefore there 
are also multiple ways to configure the tasks. In 
this section, the most common and useful ways are 
covered.

Most simplistic way to create tasks is just initiate
them in a Python source file and just import them.
However, to reduce boilder plate Red Engine also 
provide ways to load all task files using ``Loaders``.
There are essentially two types of loaders: 

- ``PyLoader``: Imports all matched Python files.
- ``TaskLoader``: Parses configuration files 

 .. _creating-task:

Creating a Task from Python Function
------------------------------------

A simple task that executes a Python function can 
be created as:

.. code-block:: python

    from redengime.tasks import FuncTask

    @FuncTask(start_cond='daily', name="my-task-1")
    def myfunc(my_session_arg, my_task_arg):
        ... # Do whatever your task is meant be done

The decorator initiates a task and sets it 
to whatever is the default session. This example runs 
once a day and is called "mytask". See for more detais: 
:py:class:`redengine.tasks.FuncTask`.

You can also organize the tasks to multiple files and 
load them using :py:class:`redengine.tasks.loaders.PyLoader`
in the setup of your session. If you used the template 
demonstrated in :ref:`getting-started` then you have this 
already set up. Alternatively you can just import all the 
files containing tasks.

Creating a Task Using Configuration Files
------------------------------------------

If you have many tasks that are meant to execute non-Python
code (such as :py:class:`redengine.tasks.Commandtask`),
it could be beneficial to configure the tasks in a configuration
file instead of in Python source files. Red Engine also has 
loader :py:class:`redengine.tasks.loaders.TaskLoader` which 
is meant to parse such tasks.

A task configuration file can look like this: 

.. code-block:: yaml

    my-task-2: # Name of the task
        class: 'FuncTask'
        func: 'myfunc'
        path: 'path/to/myfile.py'
        start_cond: 'daily'
        ... # Other FuncTask init arguments
    my-task-3:
        class: 'CommandTask'
        command: 'python -c \"open('test.txt', 'w');\"'
        start_cond: 'daily'
        ... # Other CommandTask init arguments

The first key represents the names of the tasks and 
the inner dictionary is passed to the initiation of
the task with the exception of the key ``class`` that
is used to define the actual class type. If the class 
is not specified, Red Engine tries to guess it from the 
other arguments. Also, if the key ``path`` is defined, 
its value is turned to an absolute path in case it was 
relative. This is for convenience. 

Let's call our task file as ``tasks.yaml`` and put it somewhere to 
``mytasks/`` directory. Then just load this by configuring 
a ``TaskLoader``:

.. code-block:: python

    from redengime.tasks.loaders import TaskLoader

    TaskLoader(glob='tasks.yaml', path='task/')


Arguments for Tasks
-------------------

The most commonly used arguments shared by all task classes are:

- ``start_cond``: Specifies when the task may start running. Can be a string or a condition object. 
  See: :ref:`conditions-intro`
- ``end_cond``: Specifies when the task is terminated (if running and parallerized). Can be a string or a condition object. 
  See: :ref:`conditions-intro`
- ``execution``: How the task is executed. Allowed values:
  - ``'main'``: Runs on main thread and process,
  - ``'thread'``: Runs on another thread or
  - ``'process'``: Runs on another process.
- ``parameters``: Parameters passed for specifically to this task. This is a dictionary.

Scheduling Tasks
----------------

Setting the starting and ending conditions are discussed
in :ref:`conditions-intro`.

Parallerizing Tasks
-------------------

Here is an example of all the execution options:

.. code-block:: python

    from redengime.tasks import FuncTask

    @FuncTask(execution="process")
    def my_process_task():
        ... # Do your thing.

    @FuncTask(execution="thread")
    def my_thread_task():
        ... # Do your thing.

    @FuncTask(execution="main")
    def my_main_task():
        ... # Do your thing.

There are pros and cons in each option. In short:

- Use ``process`` if your task can get stuck or 
  requires more resources and needs own process.
- Use ``main`` or ``thread`` if the task needs 
  to modify or inspect the other tasks or the 
  scheduling session. 
- Use ``thread`` or ``process`` if the task needs 
  to be permanently running.
- Use ``main`` if you need to put the scheduler 
  on hold for some reason till the task finishes.
  For example, if you are creating new tasks or 
  pipelines.

Parametrizing Tasks
-------------------

Creating and setting parameters to tasks are 
discussed in :ref:`parametrizing`.
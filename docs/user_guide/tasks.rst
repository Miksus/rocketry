.. _tasks:
 
Tasks, Basics
=============

The whole purpose of this framework is to schedule 
tasks or jobs. There are various types of tasks and 
endless ways to create new ones and therefore there 
are also multiple ways to configure the tasks. In 
this section, the most common and useful ways are 
covered.

Most simplistic way to create tasks is to create functions,
declare them as tasks and just import them to your session.
However, to reduce boilder plate Red Engine also 
provide ways to load all task files using ``Loaders``.
See :ref:`loaders` for more. 

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
once a day and is called "mytask". See for more details: 
:py:class:`redengine.tasks.FuncTask`.

You can also organize the tasks to multiple files and 
load them using :py:class:`redengine.tasks.loaders.PyLoader`
in the setup of your session. If you used the template 
demonstrated in :ref:`getting-started` then you have this 
already set up. Alternatively you can just import all the 
files containing tasks.

Arguments for Tasks
-------------------

The most commonly used arguments shared by all task classes are:

- ``name``: The name of the task. If not given, the name is derived elsewhere ie. from the name of the function.
- ``start_cond``: Specifies when the task may start running. Can be a string or a condition object. 
  See: :ref:`conditions-intro`
- ``end_cond``: Specifies when the task is terminated (if running and parallelized). Can be a string or a condition object. 
  See: :ref:`conditions-intro`
- ``execution``: How the task is executed. Allowed values:

  - ``'main'``: Runs on main thread and process.
  - ``'thread'``: Runs on another thread.
  - ``'process'``: Runs on another process (default).

- ``parameters``: Parameters passed for specifically to this task. This is a dictionary.

Scheduling Tasks
----------------

Setting the starting and ending conditions are discussed
in :ref:`conditions-intro`.

.. _parallelizing:

Parallelizing Tasks
-------------------

There are three options for how tasks are executed:

- ``process``: Run the task in a separate process.
- ``thread``: Run the task in a separate thread. 
- ``main``: Run the task in the main process and thread.

These are passed to the ``execution`` argument of a task.

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

=========== =============  =====================  ========================
Execution   Parallerized?  Can be terminated?      Can modify the session?
=========== =============  =====================  ========================
``process`` Yes            Yes                    No
``thread``  Yes            Yes if task supports   Yes
``main``    No             No                     Yes
=========== =============  =====================  ========================

.. note::

    Currently, Red Engine does not allow to have the same task running 
    multiple times at the same time as this is rarely needed and it 
    causes complications in determining what start consituted which 
    success or failure. There might or might not be support for this 
    in the future.

    If you need this, you can achieve this by duplicating the task with
    different names.

Task Statuses
-------------

There are five statuses a task may have:

- ``run``: the task is currently running
- ``fail``: the task's previous run failed
- ``success``: the task's previous run succeeded
- ``terminate``: the task's previous run was terminated
- ``inaction``: the task's previous run inacted

The first three are fairly obvious. Only the tasks that 
are running with ``thread`` or ``process`` execution may have 
``terminate`` status as ``main`` cannot be terminated. 

The status ``inaction`` is the least obvious. This status 
means that the task did not fail but it did almost nothing
due to missing data or other reasons. If you want to use 
this status, you need to raise the exception 
``rednegine.core.exceptions.TaskInactionException`` in the task's execution. It is useful
if there is a prerequisite in the task that is expensive to check
or there is a risk of getting stuck and therefore the check is 
put to the task itself.

The status of a task is found from the attribute ``task.status``.

Parametrizing Tasks
-------------------

Creating and setting parameters to tasks are 
discussed in :ref:`parametrizing`.
Welcome to :red:`Red` Engine's documentation!
=============================================

Too lazy to read? :ref:`Get started then. <getting-started>`

Red Engine is a Python scheduling library made for 
humans. It is suitable for scrapers, data processes,
process automatization or IOT applications. It also
has minimal dependencies and is pure Python.

Why :red:`Red` Engine?
----------------------

Red Engine's focus is on productivity: minimizing the 
boiler plate and maximizing the extendability. Setting
the conditions of when a task will be run and creating 
the tasks themselves are really easy things to do with 
Red Engine.

:red:`Red` Engine is useful for small to moderate size
projects. It is, however, not meant to handle thousands 
of tasks or execute tasks with the percision required 
by modern game engines.

Core Features
-------------

- **Easy setup:** Use a premade setup and focus on building your project.
- **Condition parsing:** Scheduling tasks can be done with human readable statements.
- **Parametrization:** Tasks consume session specific or task specific parameters depending on what they need.
- **Extendability:** Almost everything is made for customization. Even the tasks can modify the scheduler.

:red:`Red` Engine has built-in scheduling syntax which
allows logical operations or nesting and is easily expanded with 
custom conditions such as whether data exists in 
a database, file is found or a website is online.

Examples
--------

**Creating your tasks** with Red Engine is really simple:

.. code-block:: python

    from redengime.tasks import FuncTask

    @FuncTask(start_cond="daily between 09:00 and 14:00")
    def my_task():
        ... # Do your thing.

This task will run once a day between 9 AM and 2 PM.

**What about parametrization?**

.. code-block:: python

    from redengine.arguments import FuncArg
    from redengime.tasks import FuncTask

    @FuncTask(start_cond="daily between 09:00 and 14:00")
    def my_task(my_param):
        ... # Do your thing.

    @FuncArg.to_session()
    def my_param():
        ... # Determine the value of the parameter
        return 'my value'

The task ``my_task`` is now parametrized with whatever is returned from 
the function ``my_param``. 

**What about parallelization?**

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

The first task will run on a separate process while 
the second will run on a separate thread. The last one
is not parallelized. There are pros and cons on 
each choices. 

But does it work?
-----------------

The system is tested with over 900 unit tests to 
ensure quality of all promised features. It is already
in use.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   tutorial/index
   reference/index
   examples/index



Indices and tables
==================

* :ref:`genindex`

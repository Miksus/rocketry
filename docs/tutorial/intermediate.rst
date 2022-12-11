.. _intermediate-tutorial:

Intermediate Tutorial
=====================

This is an intermediate level tutorial.
In this tutorial we go through aspects
that you might not come across in very
simple applications but you eventually
need to know.

This tutorial includes:

- Basics of session
- Application setup
- Arguments and parametrization
- More about scheduling
- Manipulating tasks

Basics of Session
-----------------

After the application layer, the second highest level interface 
to the scheduler is the session instance. This instance 
stores the configuration options and the task themselves. It 
also provides methods to interact with the system by:

- Create and delete tasks
- Shut down or restart the scheduler
- Get the repository for task logs

This instance is accessible via an attribute in the app instance:

.. code-block:: python

    >>> from rocketry import Rocketry
    >>> app = Rocketry()
    >>> app.session

You can read more about how to use this from the 
:ref:`cookbook, control runtime <cookbook-control-runtime>`.

App Setup
---------

Rocketry application has several configuration options
which you can change to alter the behaviour of the scheduling. 
There is also the task logger to be configured so that there 
is persistence in the logs.

The configuration options can be passed with the app initiation:

.. code-block:: python

    from rocketry import Rocketry

    app = Rocketry(execution="async")

You can read more about the different options from 
:ref:`config-handbook`. 

Furthermore, you can also use the ``app.setup`` hook to set the 
configuration options:

.. code-block:: python

    from rocketry import Rocketry

    app = Rocketry()

    @app.setup()
    def setup_app():
        app.session.config.execution = "async"

In the above we created a setup hook function called ``setup_app``.
This function is called in the startup stage of the scheduler
just before any task is run. 

It is recommended to set up your application using a setup hook to
keep all the configuration logic in the same place. You can also 
setup the task logger in the hook:

.. code-block:: python

    from rocketry import Rocketry
    from rocketry.args import TaskLogger
    from rocketry.log import MinimalRecord

    from redbird.repos import CSVFileRepo

    app = Rocketry()

    @app.setup()
    def setup_app(task_logger=TaskLogger()):
        repo = CSVFileRepo(filename="logs.csv", model=MinimalRecord)
        task_logger.set_repo(repo)

Above, we used Rocketry's argument system: the value of ``task_logger``
is set dynamically when the hook is called. The value of this argument 
will be Rocketry's logging adapter which has some additional methods to
basic logger such as ``set_repo`` to set the data store for the log records.

We will go to the arguments a bit later but here is an advanced demonstration
of how you can use the setup hook:

.. code-block:: python

    from rocketry import Rocketry
    from rocketry.args import Config, TaskLogger, EnvArg
    from rocketry.log import MinimalRecord

    from redbird.repos import CSVFileRepo, MemoryRepo

    app = Rocketry()

    @app.setup()
    def setup_app(env=EnvArg("ENV", default="test"), task_logger=TaskLogger(), config=Config()):

        # Common configurations
        config.execution = "async"

        # Env dependent configurations
        if env == "prod":
            repo = CSVFileRepo(filename="logs.csv", model=MinimalRecord)
            task_logger.set_repo(repo)
            config.silence_cond_check = True
        else:
            # test or dev env
            repo = MemoryRepo(model=MinimalRecord)
            task_logger.set_repo(repo)
            config.silence_cond_check = False

The above uses different configurations depending on whether the 
environment variable *ENV* has value *prod* or something else. It 
also uses different data stores for the logs depending on the environment.

You can read more about setting up application from 
:ref:`the app settings cookbook <app-settings-cookbook>`.

Arguments
---------

Rocketry has a dynamic argument system in which 
arguments for tasks, custom conditions etc. can be 
passed indirectly. We used such arguments in the 
previous example in the application setup.

There are various places where you can use the 
dynamic argumets:

- Tasks parameters
- Hooks (such as ``@app.setup()``)
- Custom conditions
- Custom arguments

Here is a simple example of using such an argument:

.. code-block:: python

    from rocketry.args import SimpleArg

    @app.task()
    def do_things(myarg=SimpleArg('Hello world')):
        ...

When this task runs the value of ``myarg`` will be
``"Hello world"`` (and not the instance of ``SimpleArg``).
``SimpleArg`` does nothing interesting but the key take away 
is that the value is dynamic and determined by Rocketry when 
the task is stated.

More useful example would be to use ``FuncArg``:

.. code-block:: python

    from rocketry.args import FuncArg

    def get_item():
        return 'hello world'

    @app.task()
    def do_things(myarg=FuncArg(get_item)):
        ...

In the above example the ``myarg`` will get the return value of
the function ``get_item``. This function is run just before the 
task ``do_things`` is started.

.. note::

    You can also pass the arguments in the ``app.task(...)``:

    .. code-block:: python

        @app.task(parameters={"myarg": FuncArg(get_item)})
        def do_things(myarg):
            ...

There are various different types of arguments you can use.
You can also create your own arguments if needed.

There are also session level parameters which can also 
be used as input arguments for tasks or other components:

.. code-block:: python

    from rocketry.args import Arg

    # Setting parameters to the session
    app.params(session_arg='Hello world')

    @app.task()
    def do_things(myarg=Arg('session_arg')):
        ...

The value of ``myarg`` will also be ``"Hello world"``
which is stored in the session parameters. 
This is useful if you have a global argument that 
is used throughout the system. Furthermore, 
even the session level parameters can be arguments
themselves:

.. code-block:: python

    from rocketry.args import Arg, FuncArg

    def get_item():
        return "Hello world"
    
    app.params(session_arg=FuncArg(get_item))

    @app.task()
    def do_things(myarg=Arg('session_arg')):
        ...

You can also create your own argument which uses another argument:

.. code-block:: python

    from rocketry.args import Task, argument

    @argument()
    def last_success(task=Task()):
        return task.last_success

    @app.task()
    def do_things(success_time=last_success):
        ...

In the above example the value of the argument ``task`` in the function
``last_success`` will be the instance of the task that this Rocketry argument 
was set as an input argument to. In this case it would be the task ``do_things``.

Conditions
----------

In the previous tutorial we went through some basics
of scheduling. In this section we introduce the 
abstraction layers of conditions and how to create custom conditions.
You can read more about conditions from :ref:`condition handbook <condition-handbook>`.

There are three abstraction layers in the condition mechanics:

- :ref:`Condition syntax <condition-syntax>`
- :ref:`Condition API <condition-api>` (recommended)
- :ref:`Condition classes <condition-classes>`

It is recommended to use the condition API. Condition syntax
is useful for quick and simple scheduling but typos are not 
catched by code checkers and it has less reusability.
On the other hand, condition classes are the lowest level implementation and 
often not as intuitive to use.

Condition syntax works quite the same as the condition API
and it also supports logical operators:

.. code-block:: python

    @app.task("weekly on Monday & time of day after 10:00")
    def do_things():
        ...

You can read more from :ref:`the condition syntax handbook <condition-syntax>`.
But as mentioned, you should prefer condition API if practical.

Moreover, condition API enables you to rename and reuse conditions:

.. code-block:: python

    from rocketry.conds import daily, time_of_week

    business_daily = daily.between("08:00", "17:00") & time_of_week.between("Mon", "Fri")

    @app.task(business_daily)
    def do_a():
        ...

    @app.task(business_daily)
    def do_b():
        ...

Custom Conditions
^^^^^^^^^^^^^^^^^

At some point you might realize the built-in conditions
are lacking a condition for your use case. You can also
create custom conditions when needed:

.. code-block:: python

    from pathlib import Path
    from rocketry.conds import daily

    @app.cond()
    def file_exists():
        return Path("myfile.csv").exists()

    @app.task(daily & file_exists)
    def do_things():
        ...

Sometimes you might want to reuse your condition
and set arguments to it. That can be done by:

.. code-block:: python

    from pathlib import Path
    from rocketry.conds import daily

    @app.cond()
    def path_exists(file):
        return Path(file).exists()

    @app.task(daily & path_exists("myfile.csv"))
    def do_things():
        ...

You can also use Rocketry's arguments in the 
condition as well:

.. code-block:: python

    from pathlib import Path
    from rocketry.conds import daily
    from rocketry.args import FuncArg

    def get_report_date():
        return "Hello world"

    @app.cond()
    def file_exists(file, report_date=FuncArg(get_report_date)):
        file = file.format(report_date=report_date)
        return Path(file).exists()

    @app.task(daily & file_exists("myfile_{report_date}.csv"))
    def do_things():
        ...

.. note::

    The custom conditions don't need the application.
    If you put your conditions to other module than where the
    application is, you can use ``condition`` decorator:
    
    .. code-block:: python

        from pathlib import Path
        from rocketry.conds import condition

        @condition()
        def path_exists(file):
            return Path(file).exists()

Manipulating Tasks
------------------

Most of Rocketry's components are accessible also
during the scheduler is running. This includes tasks,
configurations and logging. Accessing tasks is especially
useful if your tasks are stored in a database and you
need to sync them, your users should be able to interact 
with the scheduler (ie. manually run tasks) or you need 
to create conditions that depend on other tasks.

For example, consider the following task:

.. code-block:: python

    from rocketry import Rocketry

    app = Rocketry()

    @app.task()
    def do_things():
        ...

You can access this task by:

.. code-block:: python

    >>> task = app.session[do_things]

.. note::

    Alternatively, you can access the 
    task using the task's name.
    Read more about the naming from the
    :ref:`task handbook <handbook-task-naming>`.

There are several interesting attributes
and methods you can use. You can 
read more about the task attributes 
from :ref:`task handbook <handbook-task-attrs>`.

Perhaps the most useful method tasks have is 
``run``. This allows you to force a task to
be run:

.. code-block:: python

    >>> task.run()

You can read more about manipulating the 
runtime from :ref:`cookbook, control runtime <cookbook-control-runtime>`.
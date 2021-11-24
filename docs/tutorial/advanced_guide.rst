.. _advanced-guide:

Advanced Guide
==============

This a more complete guide for Red Engine's features.

Structuring Your Project
------------------------

There is no forced structure your must project follow.
If you need something simple, you can put everything to 
a single file. If you need something more complex, this 
is how you could structure it:

.. code-block::

    project/
    │   __init__.py
    │   main.py
    │   parameters.py
    │
    │───tasks/
    │   │───.../
    │   │   │───tasks.py
    │   │   └───...
    │   │
    │   │───.../
    │   │   │───tasks.py
    │   │   └───...
    │   │   ...
    │
    └───models/
        │   __init__.py
        │   conditions.py
        │   hooks.py
        │   tasks.py
        │   ...

In short the files:

- ``project/main.py``: Configure the session here
- ``project/parameters.py``: Put here the session level task parameters
- ``project/tasks/.../tasks.py``: Put here the actual tasks
- ``project/models/conditions.py``: Put here your custom conditions
- ``project/models/tasks.py``: Put here your custom task classes
- ``project/models/hooks.py``: Put here your custom hooks


Configuring the Session
-----------------------

Next we will create the ``project/main.py`` file. We configure the 
session here, import the models, parameters and tasks and start the 
actual session here. Configuring session is simple:

.. code-block:: python

    from redengine import Session

    session = Session(
        scheme=['log_csv'],
        config={
            'silence_task_prerun': True,
            'silence_cond_check': True,
            'force_status_from_logs': False,
            'task_pre_exist': 'raise',
            'use_instance_naming': False,
            'cycle_sleep': None
        }
    )

We made a new session that uses CSV logging scheme and has some 
configurations. The schemes are premade setups that can be used 
to reduce the need to configure the required loggers yourself.
Read more about schemes in :ref:`logging-schemes`.

Configs
^^^^^^^

There are also some configs in sessions. These are settings that 
help to set the session to be more or less tolerant for errors.
When developing, it may be good idea to crash on situations like 
errors in condition checking or errors in parameters but for 
production you may want not want to crash the whole scheduler 
for such cases. The values we set above are the defaults which 
are used if not set.

Here is a quick description of these configurations:

- ``task_pre_exist``: What to do when creating a task which name already exists. Options:

    - ``raise``: Raise an error
    - ``replace``: Remove the previous task and add the new task to the session
    - ``ignore``: Don't set the new task to the session and leave the previous
    - ``rename``: Add number(s) to the name of the new task until it has unique name

- ``use_instance_naming``: If name not specified, use ``id(task)`` as the name of the task
- ``silence_task_prerun``: Don't crash the scheduler if a task fails outside the actual execution. Task is always logged as fail.
- ``silence_cond_check``: Don't crash the scheduler if checking a condition fails. If False, the state of a crashed condition is considered ``False``.
- ``force_status_from_logs``: Force the task related conditions always read the logs to determine the state. If false, the cached state is used if possible for optimization.
- ``cycle_sleep``: Seconds to wait after executing each cycle of tasks. By default no wait. 

Logging
^^^^^^^

You can also add your own handlers to the logger that is used to log 
the tasks. You could, for example, send filter the failures and send
them via SMTPHandler to your email or print the task log to terminal
using StreamHandler. In this demo we do the latter:

.. code-block:: python

    # Set logging
    import logging
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)-8s %(task_name)s %(message)s'))

    task_logger = logging.getLogger('redengine.task')
    task_logger.setHandler(console_handler)

You can find more information about logging in Red Engine in :ref:`logging-guide`.

Importing Models and Tasks
^^^^^^^^^^^^^^^^^^^^^^^^^^

Next we will import the custom conditions and task classes we may have:

.. code-block:: python

    # Import custom extensions
    from .models import conditions, tasks

And then we could import the tasks themselves. You could just import 
the files where the tasks are or alternatively you could use a *loader*.
Loader is a task that loads other tasks from predefined location. 
There is a loader ``PyLoader`` that imports Python files for us from 
given location which we will use so we don't need to explicitly import
every task file:

.. code-block:: python

    # We make sure the tasks are searched from the correct directory
    # in case the current working directory is set somewhere else
    from pathlib import Path
    main_directory = Path(__file__).parent

    # Automatic loader so we don't need to import
    # task files manually.
    from redengine.tasks.loaders import PyLoader
    PyLoader(path=main_directory / "tasks/", glob="**/tasks.py")

The ``PyLoader`` loads all Python files that matches 
the given glob from given path. In this case, it finds 
all tasks that are named ``tasks.py`` in ``project/tasks/``
folder.

Starting the scheduler
^^^^^^^^^^^^^^^^^^^^^^

And finally we start the scheduler:

.. code-block:: python

    # Start the session
    if __name__ == '__main__':
        session.start()

Content of main.py
^^^^^^^^^^^^^^^^^^

All set here. Now your ``main.py`` file should look like this now:

.. code-block:: python

    import logging
    from pathlib import Path

    from redengine import Session
    from redengine.tasks.loaders import PyLoader

    from .models import conditions, tasks

    session = Session(
        scheme=['log_csv'],
        config={
            'silence_task_prerun': True,
            'silence_cond_check': True,
            'force_status_from_logs': False,
            'task_pre_exist': 'raise',
            'use_instance_naming': False
        }
    )

    # Set logging    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)-8s %(task_name)s %(message)s'))

    task_logger = logging.getLogger('redengine.task')
    task_logger.setHandler(console_handler)

    # We make sure the tasks are searched from the correct directory
    # in case the current working directory is set somewhere else
    main_directory = Path(__file__).parent

    # Automatic loader so we don't need to import
    # task files manually.
    PyLoader(path=main_directory / "tasks/", glob="**/tasks.py")

    # Start the session
    if __name__ == '__main__':
        session.start()


Tasks
-----

Next we will create some tasks. Put these to the ``tasks.py``
files in ``project/tasks/`` directory, for example 
``project/tasks/scrapers/tasks.py``. We made some simple tasks
already in :ref:`short-guide` but now we will discuss them more thorougly.
Here is a practical example of such file:

.. code-block:: python

    from redengine.tasks import FuncTask

    @FuncTask(start_cond="daily after 08:00")
    def wake_up():
        ... # Code to make you woke

    @FuncTask(start_cond="daily between 08:00 and 08:15 | daily between 22:00 and 22:15")
    def wash_teeth():
        ... # Code to wash your teeth twice a day

    @FuncTask(start_cond="daily between 09:00 and 10:00 & time of week between Monday and Friday")
    def go_to_work():
        ... # Code to work

We made couple of tasks that run as follows:

- ``wake_up``: Runs once a day between 8 AM and 12 PM
- ``wash_teeth``: Runs twice a day. Once between 08:00 AM to 08:15 AM and once between 10:00 PM and 10:15 PM
- ``do_work``: Runs once a day between 9 AM and 10 AM but only on week days.

Using ``&`` (and) and ``|`` (or) operators we can create more complex scheduling logic than individual 
conditions allow. We made the task ``wash_teeth`` to run twice a day using the *or* operator and 
further constrained the time the task ``go_to_work`` may run using the *and* operator. You can also 
nest these operations using parentheses (ie. ``... & (... | ...)``).
 
Pipelining
^^^^^^^^^^

You can also create task pipelines conveniently. Let's make a file ``project/tasks/pipelines/tasks.py``
to demonstrate this:

.. code-block:: python

    from redengine.tasks import FuncTask

    @FuncTask()
    def get_data():
        ... # Code to get data

    @FuncTask(start_cond="after task 'get_data' succeeded")
    def transform_data():
        ... # Code to transform data

    @FuncTask(start_cond="after task 'transform_data'")
    def store_data():
        ... # Code to store data (runs if transform_data succeeded)

    @FuncTask(start_cond="after task 'get_data' failed")
    def report_errors():
        ... # Code to report errors in getting data

You can find more about pipelining from :ref:`pipeline-guide`. and more about different condition options
from :ref:`condition-syntax`. You can also find more information about conditions from :ref:`conditions-intro`.

Execution
^^^^^^^^^

Next we will make some more tasks (let's say to ``project/tasks/checks/tasks.py``) to discuss some other features:

.. code-block:: python

    from redengine.tasks import FuncTask

    @FuncTask(start_cond="minutely", execution="main")
    def check_pulse():
        ... # Code to check pulse

    @FuncTask(start_cond="hourly", execution="thread")
    def check_emails():
        ... # Code to check emails

    @FuncTask(start_cond="weekly", execution="process")
    def check_mail():
        ... # Code to check mails

Note that we used different ``execution`` for these tasks. 
``check_pulse`` will run on the main process and thread
(no parallelization), ``check_emails`` will run on a 
separate thread and ``check_mail`` will run on a separate
process. There are advantages and disadvantages in each and
they are further discussed in :ref:`parallelizing`. In short,
``process`` allows the most parallelization but is the most 
expensive in terms of initiation. It is also the default if not 
specified. It also allows you to terminate tasks 
and have timeouts like:

Terminating
^^^^^^^^^^^

.. code-block:: python

    @FuncTask(start_cond="weekly", execution="process", timeout="2 hours")
    def check_mail():
        ... # Code to check mails

Alternatively, you can have a condition that defines when the task will
be terminated:

.. code-block:: python

    @FuncTask(start_cond="weekly", execution="process", end_cond="time of day between 16:00 and 20:00")
    def check_mail():
        ... # Code check messages

Parametrization
^^^^^^^^^^^^^^^

And finally, we make some parameterized tasks to, let's say, 
``project/tasks/send/task.py``:

.. code-block:: python

    from redengine.tasks import FuncTask

    @FuncTask(parameters={"receivers": ['me@example.com']})
    def report_news(receivers):
        ... # Code to send news

    @FuncTask()
    def announce(friend_list):
        ... # Code to send an announcement

The function ``report_news`` has parameter ``receivers``
and this parameter will have value ``['me@example.com']``.
However, the task ``announce`` requires a parameter 
``friend_list`` which we did not yet define. Red Engine also 
has session wide parameters which are automatically fed to 
tasks that require given parameter and don't have it set 
yet. Next we will create the logic to feed this parameter
``friend_list``  

You can also use the output of a task as an input for 
another task:

.. code-block:: python

    from redengine.tasks import FuncTask

    @FuncTask()
    def get_data():
        ... # Code to get data
        return data

    @FuncTask(parametes={"my_data": Return('get_data')})
    def process_data(mydata):
        ... # Code to process data

When the task ``process_data`` executes, the argument ``mydata``
will get the return value of the task ``get_data`` as the value.
In case ``get_data`` did not run before ``process_data``, the 
argument will receive a value ``None``. 

Parameters
----------

Following the previous example about the ``announce`` task, we will create a function 
that acts as our parameter ``friend_list``. Let's put it in
the file ``project/parameters.py``:

.. code-block:: python

    from redengine.parameters import FuncParam

    @FuncParam()
    def friend_list():
        # Code to come up with friend list
        return []

Just remember to import this to the file where you have your
session. This function is automatically run right before 
executing the tasks that require this parameter and the return
value of this function is used as the parameter value.

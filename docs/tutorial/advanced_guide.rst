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
- ``project/parameters.py``: Put here the session parameters for tasks
- ``project/tasks/.../tasks.py``: Put here the actual tasks
- ``project/models/conditions.py``: Put here your custom conditions
- ``project/models/hooks.py``: Put here your custom hooks

Your ``main.py`` file could look like:

.. code-block:: python

    from redengine import session

    # Import custom extensions
    from .models import conditions, tasks


    # Set logging
    import logging
    from redengine.log import CsvHandler, CsvFormatter
    
    task_handler = CsvHandler(fields=[
        task_name,
        asctime,
        action,
        start, # Start of the task
        end, # End of the task ('run' does not have end)
        runtime,
        message
    ])
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)-8s %(task_name)s %(message)s'))

    task_logger = logging.getLogger('redengine.task')
    task_logger.setHandler(task_handler)
    task_logger.setHandler(console_handler)
    task_logger.setLevel(logging.INFO)


    # Automatic loader so we don't need to import
    # task files manually.
    from redengine.tasks.loaders import PyLoader
    PyLoader(path="tasks/", glob="**/tasks.py")

    # Start the session
    if __name__ == '__main__':
        session.start()

In this example we use ``PyLoader`` to load our task files
but you can also just import them yourself to the Python
file where you have your session. In our example, the tasks
are located in files named as ``tasks.py`` somewhere in the 
``project/tasks/`` directory.

In addition, we use ``CsvHandler`` to log when tasks have been
run, succeeded, failed or terminated. Alternatively, you could 
also just use the ``redengine.log.MemoryHandler`` if you want
to have the logs in memory or you can create your own handler.
Just remember to include a ``.read()`` method that should return
the log records as list of dicts or ``.query(...)`` method if 
you want to handle the filtering of records yourself.

As Red Engine's logging is built completely on Python's ``Logging``
library found in standard library, you can extend and have 
any kind of logging strategies as far as there is one readable 
logger for ``redengine.tasks`` logger.

Tasks
-----

Next we will create some tasks. Put these to the ``tasks.py``
files in ``project/tasks/`` directory, for example 
``project/tasks/scrapers/tasks.py``. We made some simple tasks
in :ref:`short-guide` but we will discuss them more thorougly.
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

We made couple of tasks that runs as follows:

- ``wake_up``: Runs once a day between 8 AM and 12 PM
- ``wash_teeth``: Runs twice a day. Once between 08:00 AM to 08:15 AM and once between 10:00 PM and 10:15 PM
- ``do_work``: Runs once a day between 9 AM and 10 AM but only on week days.

As you probably noted, using ``&`` (and) and ``|`` (or) operators we can have pretty complex scheduling logic
but still be fairly understandable to read. We used ``|`` operator to expand the time when ``wash_teeth``
may run and ``&`` to further constain the time when ``go_to_work`` may run. You can build any logic you want
and use parentheses (ie. ``... & (... | ...)``) to further manipulate how you schedule things. 
 
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

You can also built logic with ``&`` and ``|`` to run a task, for example, 
after multiple tasks have all succeeded or when any of a list of tasks is 
succeeded. 

See more condition options for ``start_cond`` in :ref:`condition-syntax` and read more about conditions 
from :ref:`conditions-intro`.

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
``process`` allows the most parallelization and that is also
the default if not specified. Execution ``process`` also allows
you to terminate tasks and have timeouts like:

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

Finally, we make some parameterized tasks to, let's say, 
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

Parameters
----------

Following the previous example, we will create a function 
that acts as our parameter ``friend_list``. Let's put it in
the file ```project/parameters.py```:

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

.. _scheduling:

Scheduling
==========

In Red Engine, tasks are scheduled by setting
start conditions or triggers to tasks. These 
are simply statements that are ``True`` or 
``False``. Conditions are explained with greater 
detail in :ref:`conditions-intro`. In this section 
the scheduling is explained in more practical terms.

Setting Starting Condition
--------------------------

You can pass the condition object to the initiation
of a task but there is also a powerful condition 
parser:

.. code-block:: python

    from redengine.tasks import FuncTask

    @FuncTask(start_cond="time of day 09:00 and 16:00")
    def be_alive():
        ... # Do whatever

This task called ``be_alive`` will be run  when time of day 
is between 9 AM and 4 PM. Note that the task will 
start again constantly during when the current time is as specified. 
To solve this, Red Engine provides intuitive conditions to make sure 
the task runs only once in the given period:

.. code-block:: python

    @FuncTask(start_cond="daily between 09:00 and 16:00")
    def do_daily_task():
        ... # Do whatever

This task will run only once a day between 9 AM 
and 4 PM. 

Alternatively, you can also have the same outcome
with:

.. code-block:: python

    @FuncTask(start_cond="~has finished today & time of day between 09:00 and 16:00")
    def do_daily_task():
        ... # Do whatever

In plain English, this task runs when this task has not
succeeded nor failed today (``~`` is a NOT operator) and
the current time is between 9 AM and 16 PM (``&`` is an AND
operator). As you can see, Red Engine allows using logical 
operations creating huge variety of ways to schedule tasks. 
You can also combine conditions with a symbol ``|`` (``OR``)
and the parser accepts parentheses (``(...)``) to create 
complex scheduling logic.

Condition Options
-----------------

Also the individual condition items have different parametrization
options. For example, if you simply want to run a task daily, you
can have a starting condition of ``daily`` but you can also specify
the time of day the task is allowed to be run, like ``daily between
09:00 and 16:00`` or you can run it daily but also specify when a day 
is considered to start, like ``daily starting 06:00``.

See: :ref:`condition-syntax` for more details about different 
scheduling syntax.

Some generic examples (choose an option in square brackets and 
fill in values for ``<start>``, ``<end>``, ``<value>`` and 
``<timedelta>``):

- ``[hourly | daily | weekly | monthly]``
- ``[hourly | daily | weekly | monthly] between <start> and <end>``
- ``[hourly | daily | weekly | monthly] [before | after | starting] <time>``
- ``every <timedelta>``

- ``time of [hour | day | week | month] between <start> and <end>``
- ``time of [hour | day | week | month] [after | before] <time>``

- ``has [succeeded | failed | started] [this hour | today | this week] between <start> and <end>``
- ``has [succeeded | failed | started] [this hour | today | this week] [before | after] <time>``
- ``has [succeeded | failed | started] past <timedelta>``

- ``after task '<task>'``
- ``after task '<task>' [succeeded | failed | finished | terminated]``

Example Patterns (time)
-----------------------

Run once a day:

.. code-block:: python

    @FuncTask(start_cond="daily")
    def do_things():
        ... # Do whatever

Run once a day on week days:

.. code-block:: python

    @FuncTask(start_cond="daily & time of week between Monday and Friday")
    def do_things():
        ... # Do whatever

Run once a week on Tuesday after 10 AM:

.. code-block:: python

    @FuncTask(start_cond="time of week on Tuesday & time of day after 10:00")
    def do_things():
        ... # Do whatever

Run twice a week on Monday and on Friday. Run before 8 AM on Monday and after 10 PM
on Friday:

.. code-block:: python

    @FuncTask(start_cond="""
        (weekly on Monday & time of day before 08:00) 
        | (weekly on Friday & time of day after 20:00)
    """)
    def do_things():
        ... # Do whatever


Example Patterns (task)
-----------------------

Run after task named "another task" has succeeded before 
this task:

.. code-block:: python

    @FuncTask(start_cond="after task 'another task'")
    def do_things():
        ... # Do whatever

or the "another task" failed before this task:

.. code-block:: python

    @FuncTask(start_cond="after task 'another task' failed")
    def do_things():
        ... # Do whatever

Run after both tasks ``x`` and ``y`` have succeeded before this 
task:

.. code-block:: python

    @FuncTask(start_cond="after task 'x' & after task 'y'")
    def do_things():
        ... # Do whatever

Run after either task ``x`` or task ``y`` has succeeded before this 
task:

.. code-block:: python

    @FuncTask(start_cond="after task 'x' | after task 'y'")
    def do_things():
        ... # Do whatever


Example Patterns (complex)
--------------------------


Run hourly but if the task fails, don't run for 7 days:

.. code-block:: python

    @FuncTask(start_cond="every 1 hour & ~has failed past 7 days")
    def do_things():
        ... # Do whatever

Extending
---------

If there is missing a condition for your case, you can easily
create such and even have it included to the parsing engine. 
See :ref:`cust-cond` for more.
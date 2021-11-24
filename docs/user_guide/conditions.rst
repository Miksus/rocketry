.. _conditions-intro:

Conditions, Basics
==================

Conditions are vital part of Red Engine system
as they are responsible of determining when a 
task may start. They also can be used to determine
when the session will end or when a (parallelized) 
task should be killed. 

A condition can be either ``true`` or ``false``.
They can represent, for example, statement of 
current time (ie. it is afternoon now), a statement 
about a state (ie. the machine has internet access), 
presence of an event (ie. a task has successfully run) 
or presence of an thing (ie. a file exists).

There are two ways of creating conditions:

- Using Red Engine's string parser or
- Creating them from Red Engine's condition classes

The former is meant for being as human readable
and convenient as possible. Therefore this method 
is preferred and this section mostly covers that.

The conditions can be set to the tasks' initiation 
arguments directly as strings:

.. code-block:: python

    FuncTask(..., start_cond="daily between 10:00 and 14:00")

or you can set them to the ``start_cond`` of a task 
configuration file if that is preferred. To refresh how to 
set up tasks, see :ref:`creating-task`. The next examples 
can be directly supplied to the ``start_cond`` or to the 
``end_cond`` of a task.


Combining Conditions with Logic
-------------------------------

Conditions can also be combined using boolean logic. The 
conditions support the following operators: 

- ``&``: **AND** operator 
- ``|``: **OR** operator 
- ``~``: **NOT** operator

For example, ``<condition A> & <condition B>`` mean that the
statement is true only if both conditions (A and B) are true. 
Similarly ``<condition A> | <condition B>`` mean that either
A or B need to be true for the whole statement to be true and 
``~<condition A>`` mean that A must be false for the 
statement to be true. The operators can also be nested using 
parentheses.

In practice, this looks like:

.. code-block:: python

    FuncTask(..., start_cond="""
        (time of day between 08:00 and 10:00 & time of week between Monday and Friday) 
        | (time of day between 14:00 and 16:00 & ~time of week between Monday and Friday)
    """)

The starting condition of this task is ``True`` if the time is between 8 AM and 10 AM and 
current day is a week day or if the time is between 2 PM and 4 PM and current day is a non 
week day (weekend). There are more elegant ways to express the same but this is for the 
sake of example. Any condition can be combined with the same operators and next we will 
discuss about some useful conditions found from Red Engine.

.. _conditions-examples:

Conditions, Examples
--------------------

The syntax are specified in the section :ref:`condition-syntax`. There are several types
of built-in conditions useful for various scheduling strategies:

- See :ref:`cond-execution` if you want to run a task in specific fixed intervals (ie. hourly, daily, weekly).
- See :ref:`cond-timedelta` if you want to run a task after specific amount of time has passed (ie. a minute, an hour a day).
- See :ref:`cond-dependence` if you want to run a task after another task has succeeded, failed or both.
- See :ref:`cond-status` or :ref:`cond-fixedinterval` if you want to combine and create more advanced logic  
  with task statuses and time of day.


Next possibly the most common patterns are shown.


Time Related
^^^^^^^^^^^^

.. literalinclude:: /examples/conditions/time.py
    :language: py

Task Related
^^^^^^^^^^^^

.. literalinclude:: /examples/conditions/task.py
    :language: py


Custom Condition
----------------

Easiest way to create your own condition that can 
be used in the ``start_cond`` argument of a task is 
to simply create a function and decorate it using
``FuncCond``:

.. code-block:: python

    from redengine.conditions import FuncCond

    @FuncCond(syntax="is foo")
    def is_foo():
        ... # Logic to check the condition's status
        return True

Then we can immediately use it as:

.. code-block:: python

    from redengine.tasks import FuncTask

    @FuncTask(start_cond="is foo")
    def do_foo():
        ... # Runs when function is_foo returns True

The argument ``syntax`` can be a string, regex pattern
(``re.compile(...)``) or a list of them. This is fed to 
the string parser so it knows how to parse such. The 
function must return ``True`` or ``False`` depending on
whether the condition is true or not. 

The named groups of a regex (if there are any) will be 
passed to the function. Therefore, you can also do more 
complex conditions like:

.. code-block:: python

    import re

    @FuncCond(syntax=re.compile("is foo (?P<place>.+"))
    def is_foo_where(place):
        if place == "home":
            return True
        else:
            return False

And to use this:

.. code-block:: python

    from redengine.tasks import FuncTask

    @FuncTask(start_cond="is foo home")
    def do_foo():
        ... # Runs when is_foo(place='home') returns True
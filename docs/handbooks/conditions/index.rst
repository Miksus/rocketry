.. _condition-handbook:

Conditions
==========

Rocketry's scheduling system works with conditions
that are either true or false. A simple condition
could be *time is now between 8 am and 2 pm* (12-hour clock) 
or *time is now between 08:00 and 14:00* (24-hour clock).
If current time is inside this range, the condition
is true and if not, then it's false. If this is a condition 
for a task, the task is run if the the current time is in the range. 

The conditions can be combinded using logical operations:
**AND**, **OR**, **NOT**. They also can be nested using 
parentheses.

There are three ways of creating conditions in Rocketry:

- :ref:`Condition syntax <condition-syntax>`
- :ref:`Condition API (recommended) <condition-api>`
- :ref:`Condition classes <condition-classes>`

All of the above generate condition instances that 
can be used as:

- The start condition of a task (task starts if the condition is true)
- The end condition of a task (task terminates if the condition is true and the task is running)
- The shut condition of the scheduler (scheduler shuts down if the condition is true, useful in testing)

When evaluating a condition, the system uses method ``observe`` to get 
the state of the condition. You can test the status of a condition by:

.. code-block:: python

    >>> from rocketry.conds import time_of_day
    >>> condition = time_of_day.between("10:00", "14:00")
    >>> condition.observe()
    True

The above returns ``True`` if your current time is between 10:00 (10 AM) and 14:00 (2 PM).
Some conditions might rely on a task or the session 
(passed as ``.observe(task=task, session=session)``).

The built-in conditions can be put to the following categories:

* Time-based conditions

  * Floating time conditions (such as *every 10 seconds*)
  * Fixed time conditions (such as *daily*, *weekly*)

    * Task and time dependent (true if the current time is in the period and the task has not run on the period)
    * Time dependent (true if the current time is in given period)

* Task dependent (such as after a task succeeded)
* Miscellaneous

.. toctree::
   :maxdepth: 3
   :caption: Contents:

   api/index
   syntax/index
   classes/index
   comparisons
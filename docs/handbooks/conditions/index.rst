.. _condition-handbook:

Conditions
==========

Rocketry's scheduling system works with conditions
that are either true or false. A simple condition
could be *time is now between 8 am and 2 pm* (12-hour clock) 
or *time is now between 08:00 and 14:00* (24-hour clock).
If current time is inside this range, the condition
is true and if not, then it's false. If this is a condition 
for a task, it runs if the the current time is in the range. 

The conditions can be combinded using logical operations:
**AND**, **OR**, **NOT**. They also can be nested using 
parentheses.

There are three ways of creating conditions in Rocketry:

- Condition syntax
- Condition API
- Condition classes

All of the above produce instances of conditions that 
can be used as the starting conditions of tasks or the 
shut down condition of a scheduler. The condition syntax 
turns the condition strings to the condition API's 
components and condition API's components are turned to
instances of the actual conditions.


Logical Operators
-----------------

Logical operators enable to extend the existing
conditions and create more complex scheduling 
patterns. The <SECTION> supports three logical operators:

- ``&``: **AND** operator
- ``|``: **OR** operator
- ``~``: **NOT** operator

It also supports parentheses to nest the conditions.

.. raw:: html

   <details>
   <summary><a>Condition Syntax</a></summary>

.. literalinclude:: /code/conds/syntax/logic.py
    :language: py

.. raw:: html

   </details>

.. raw:: html

   <details>
   <summary><a>Condition API</a></summary>

.. literalinclude:: /code/conds/api/logic.py
    :language: py

.. raw:: html

   </details>


Floating Period Scheduling
--------------------------

Perhaps the most common scheduling problem is to run
a task after a specific time has passed.

.. raw:: html

   <details>
   <summary><a>Condition Syntax</a></summary>

.. literalinclude:: /code/conds/syntax/every.py
    :language: py

.. raw:: html

   </details>

.. raw:: html

   <details>
   <summary><a>Condition API</a></summary>

.. literalinclude:: /code/conds/api/every.py
    :language: py

.. raw:: html

   </details>


Fixed Period Scheduling
-----------------------

It is also common to have a task to run once in some 
agreed fixed time span. Such time spans are:

- hour: starts at 0 minute and ends at 60 minute
- day: starts at 00:00 and ends at 24:00
- week: starts on Monday at 00:00 and ends on Sunday at 24:00
- month: starts at 1st at 00:00 and ends 28rd-31st at 24:00

Running a task every hour is different than running a task
hourly in Rocketry. The difference is that the former runs
every time after 60 minutes has passed but the latter every
full hour. If time is now 07:15, the former will run at 
08:15 but the latter will run at 08:00.


.. raw:: html

   <details>
   <summary><a>Condition Syntax</a></summary>

.. literalinclude:: /code/conds/syntax/periodical.py
    :language: py

.. raw:: html

   </details>

.. raw:: html

   <details>
   <summary><a>Condition API</a></summary>

.. literalinclude:: /code/conds/api/periodical.py
    :language: py

.. raw:: html

   </details>


Constrained Fixed Period Scheduling
-----------------------------------

The fixed periods can also be constrained using ``before``,
``after`` and ``between``:

- ``before``: From the beginning of the fixed period till the given time
- ``after``: From the given time to the end of the fixed period
- ``between``: From given start time to the given end time

So what this means in practice? Here is an illustration for a day/daily:

- *before 14:00*: From 00:00 (0 am) to 14:00 (2 pm)
- *after 14:00*: From 14:00 (2 pm) to 24:00 (12 pm)
- *between 08:00 and 16:00*: From 08:00 (8 am) to 16:00 (4 pm)

and some illustations what this means for a week/weekly:

- *before Friday*: From Monday 00:00 (0 am) to Friday 24:00 (12 pm)
- *after Friday*: From Friday 00:00 (0 am) to Sunday 24:00 (12 pm)
- *between Tuesday and Friday*: From Tuesday 00:00 (0 am) to Friday 24:00 (12 pm)

There are also *on* and *starting* arguments:

- ``on``: On given time component 
- ``starting``: The fixed period starts on given time 

For example, *on Friday* means Friday 00:00 (0 am) to Friday 24:00 (12 pm)
and *starting Friday* means the week is set to start on Friday.



.. raw:: html

   <details>
   <summary><a>Condition Syntax</a></summary>

.. literalinclude:: /code/conds/syntax/periodical_restricted.py
    :language: py

.. raw:: html

   </details>

.. raw:: html

   <details>
   <summary><a>Condition API</a></summary>

.. literalinclude:: /code/conds/api/periodical_restricted.py
    :language: py

.. raw:: html

   </details>



.. note::

    The logic follows natural language. Statement 
    ``between Monday and Friday`` means Monday at 00:00
    (0 am) to Friday 24:00 (12 pm).

There are also **time of ...** conditions check if the current time
is within the given period.



.. raw:: html

   <details>
   <summary><a>Condition Syntax</a></summary>

.. literalinclude:: /code/conds/syntax/time_of.py
    :language: py

.. raw:: html

   </details>

.. raw:: html

   <details>
   <summary><a>Condition API</a></summary>

.. literalinclude:: /code/conds/api/time_of.py
    :language: py

.. raw:: html

   </details>



Pipelining Task
---------------

There are also conditions related to if another task has 
runned/succeeded/failed before the task we are setting the
starting condition. These are useful for creating task 
depenencies or task pipelines. 



.. raw:: html

   <details>
   <summary><a>Condition Syntax</a></summary>

.. literalinclude:: /code/conds/syntax/pipe_single.py
    :language: py

.. raw:: html

   </details>

.. raw:: html

   <details>
   <summary><a>Condition API</a></summary>

.. literalinclude:: /code/conds/api/pipe_single.py
    :language: py

.. raw:: html

   </details>



You can also pipe multiple at the same time to avoid long
logical statements:



.. raw:: html

   <details>
   <summary><a>Condition Syntax</a></summary>

.. literalinclude:: /code/conds/syntax/pipe_multiple.py
    :language: py

.. raw:: html

   </details>

.. raw:: html

   <details>
   <summary><a>Condition API</a></summary>

.. literalinclude:: /code/conds/api/pipe_multiple.py
    :language: py

.. raw:: html

   </details>



.. toctree::
   :maxdepth: 3
   :caption: Contents:

   syntax
   api
   classes
   comparisons
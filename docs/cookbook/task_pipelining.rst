Task Pipelining
===============

Rocketry supports two types of task pipelining:

- Run a task after another task has succeeded or failed
- Put the return or output value of a task as an input argument to another

Run Task After Another Task
---------------------------

You can use conditions ``after_...`` to set a task 
to be run after another task has succeeded or failed. 

Here are some examples:

.. literalinclude:: /code/conds/api/pipe_single.py
    :language: py

There are also conditions ``after_all_...`` and ``after_any_...``
if you have a lot of dependent tasks:

.. literalinclude:: /code/conds/api/pipe_multiple.py
    :language: py

Set Task Output as an Input
---------------------------

You can also set the output of a task as an input for another
task. You can use the argument ``Return`` for this purpose:

.. literalinclude:: /code/params/return.py
    :language: py

Combining Both
--------------

You can also set a task to be run after another task and 
also set the output of the latter as an input for the former:

.. literalinclude:: /code/conds/api/pipe_with_return.py
    :language: py

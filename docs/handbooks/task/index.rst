
Task
====

In this handbook we go through some technical details of 
how the tasks works and how to change their behaviour.

.. _handbook-task-attrs:

Attributes
----------

Here is a list of the most useful task attributes:

**name**: Name of the task.

**execution**: Execution type of the task.

    By default, uses session configuration default.

**multilaunch**: Whether to allow multilaunch.

    If ``True``, the task can be run parallel against 
    itself. By default, uses the value specified in the 
    session configurations.

**last_run**: Last datetime the task started.

**last_success**: Last datetime the task succeeded.

**last_fail**: Last datetime the task failed.

**last_terminate**: Last datetime the task terminated.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   naming
   termination
   execution
   observer
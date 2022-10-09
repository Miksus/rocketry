
Task
====

In this handbook we go through some technical details of 
how the tasks works and how to change their behaviour.


Launching
---------

Rocketry's scheduler that is running on main process and thread
is responsible launching tasks. The tasks can run synchronously 
or asynchronously on separate async task, thread or process.

Typically a task cannot start if it is already running. In other words,
there is a lock that prevents parallel running of the same task. However,
this can be turned off by setting ``multilaunch=True`` on the task initiation
or in the session configurations.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   termination
   execution

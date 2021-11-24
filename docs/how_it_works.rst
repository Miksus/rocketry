

How it works?
=============

There are three core components in Red Engine's ecosystem:

- **Session**: handles the configuration and act as an interface
- **Scheduler**: handles the flow of the system
- **Task**: handles how to execute a task


Flow of the system
------------------

.. figure:: scheduling.png
   :figwidth: 1000
   :alt: system flow


Task execution
--------------

.. figure:: task_execution.png
   :figwidth: 1000
   :alt: task execution

Additional components
---------------------

There are also some components that don't define the 
flow of the system but are still important for the 
system to function or essential for many of the 
features:

- **Condition**: A statement that is true or false but the
  outcome may be dependent on time.
- **Parameters**: A container (dict) for key-value pairs 
  passed to tasks.
- **Argument**: A value of a key-value pair in Parameters.
  Useful for providing dynamics to the parametrization.
- **TimePeriod**: An abstraction of time elements to define
  time intervals and periods such as *today*, *specific time of day*,
  *week* etc.
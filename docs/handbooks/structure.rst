
Rocketry's Structure
====================

This section explains the structure of the 
framework. 

Here are the most important components 
of the framework and their short descriptions:

.. glossary::

    ``rocketry.Rocketry``

        This is the Rocketry application. This is the highest level interface to 
        the framework and it is used to create tasks, conditions and parameters
        using a simple syntax. Mostly manipulates a ``rocketry.Session`` and is 
        often called to start the scheduling session.

    ``rocketry.Session``

        This is a scheduling session that contains the tasks, parameters, 
        conditions and configurations. This is also meant to be used for 
        runtime communication with the scheduler including creating, updating or
        deleting tasks during the runtime, setting a task to run manually,
        disabling a task, shutting down or restarting the scheduler etc.

    ``rocketry.core.Scheduler``

        This is the functional scheduler. This is not meant to be interacted 
        by the user of the library.

    ``rocketry.core.Task``

        Base class for tasks. A task is a function, a command, a piece of code 
        or other piece of work. Tasks can be scheduled or they can be run 
        manually. Tasks can be set to run based on conditions. They also can 
        be terminated using timeout, conditions or user input. They also can 
        run on separate threads and processes or set running async. They also
        can be parametrized and pipelined.

    ``rocketry.core.BaseCondition``

        Base class for conditions. A condition is a statement that is either 
        true or false depending on time of day, a state or other factor.
        Conditions are used to define when a task is allowed to run, when a
        task should terminate or when the scheduler should shut down.

    ``rocketry.core.TimePeriod``

        Base class for time periods. A time period is an abstract interval that 
        has a start and an end. The start and the end may not be fixed and may depend
        on a reference date. For example, a week is an interval which start and 
        end dates depend on the year and the week number. Time periods are used 
        in scheduling to define whether a specific event, such as starting of a task, 
        happened on a given period such as time of day, day of week or month.

    ``rocketry.core.Parameters``

        Parameters is a dictionary-like class containing key-value pairs that can
        be used as the input arguments for tasks. The keys of the pairs represent
        names of the arguments and the values are either actual values inputted to 
        tasks or instances of ``BaseArgument``'s subclasses.

    ``rocketry.core.BaseArgument``

        Base class for abstracted arguments. An argument is a value that can be inputted 
        to tasks. The instances of this class represent abstracted values which are 
        turned actual values when the task is about to be executed. The actual value of
        an argument can be a return value of a function, a return value of another task
        or it can be defined with other logic.  


Layers of Abstraction
---------------------

Rocketry is a complex framework but it is clean and simple on the surface. 
This is done by having multiple levels of abstraction. The different 
abstraction levels are for encapsulating complex core mechanics to 
simpler form but also for fulfilling the needs of basic, intermediate
and advanced users.

The scheduling has three layers:

- ``rocketry.Rocketry``: This is meant as the high level interface.
- ``rocketry.Session``: This is meant for runtime communication and it contains the 
  scheduling session's information.
- ``rocketry.core.Scheduler``: This is the low level functional scheduler.
  This class is contains the main loop that handles the scheduler itself
  and it is not meant to be interacted by the user of the framewrok.


The conditions also have three layers of abstraction:

- **Condition syntax**: This is a string based scheduling language.
  It is meant to be close to natural language and it is useful for 
  smaller projects.
- **Condition API**: This is a medium-level interface to create 
  conditions. Useful for most cases.
- **Condition classes**: Actual conditions. Mostly meant to be 
  created using the condition API or condition syntax.


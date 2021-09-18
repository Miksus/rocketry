Welcome to :red:`Red` Engine's documentation!
=============================================

Red Engine is a Python scheduling library made for 
humans. The goal is to make scheduling tasks
as intuitive and convenient as possible while providing 
the maximum amount of customization. 

Some core features of :red:`Red` Engine include:

- **Easy setup:** Yse a premade setup and focus on building your project.
- **Condition parsing:** Scheduling tasks can be done with human readable statements.
- **Parametrization:** Tasks consume session specific or task specific parameters depending on what they need.
- **Extendability:** Almost everything is made for customization. Even tasks can modify the scheduler.

:red:`Red` Engine has built-in scheduling syntax which
allows logical operations or nesting and is easily expanded with 
custom conditions such as whether data exists in 
a database, file is found or a website is online.

Examples of condition syntax:
-----------------------------

- Run once a day after 2 PM
    - ``daily after 02:00``
- Run twice a week: on monday and on friday between 10 AM and 3 PM.
    - ``time of day between 10:00 and 15:00 & (weekly on Monday | weekly on Friday)``
- Run once after task `fetch-stuff` has succeeded or `fetch-things` have failed
    - ``after task 'fetch-stuff' succeeded | after task 'fetch-things' failed``


Philosophy
----------

- **Tasks are first class citizens.** 
    - Tasks have the possibility to access and modify all of the data in the system.
- **Reuse is a virtue.** 
    - For example, the logging library is extended for handling reading the task logs. 
      Therefore Red Engine links seamlessly to the mechanisms of the logging library.
- **If it's not intuitive, it's not used.** 
    - The framework is made as convenient as possible for the user.
- **If it's not extendable, it will not evolve.** 
    - Almost everything is a building block made for modifications.
- **If it's not tested, it's broken.** 
    - Red Engine contains more than 700 unit tests to ensure the system works as promised.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   tutorial/index
   reference/index
   extending


Indices and tables
==================

* :ref:`genindex`

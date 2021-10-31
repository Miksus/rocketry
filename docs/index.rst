Welcome to :red:`Red` Engine's documentation!
=============================================

Too lazy to read? :ref:`Get started then. <getting-started>`

Red Engine is a Python scheduling library made for 
humans. It is suitable for scrapers, data processes,
process automatization or IOT applications. It also
has minimal dependencies and is pure Python.

Why :red:`Red` Engine?
----------------------

Red Engine's focus is on productivity: minimizing the 
boiler plate and maximizing the extendability. Setting
the conditions of when a task will be run and creating 
the tasks themselves are really easy things to do with 
Red Engine.

:red:`Red` Engine is useful for small to moderate size
projects. It is, however, not meant to handle thousands 
of tasks or execute tasks with the percision required 
by modern game engines.

Core Features
-------------

- **Easy setup:** Use a premade setup and focus on building your project.
- **Condition parsing:** Scheduling tasks can be done with human readable statements.
- **Parametrization:** Tasks consume session specific or task specific parameters depending on what they need.
- **Extendability:** Almost everything is made for customization. Even the tasks can modify the scheduler.

:red:`Red` Engine has built-in scheduling syntax which
allows logical operations or nesting and is easily expanded with 
custom conditions such as whether data exists in 
a database, file is found or a website is online.

Example
-------

This is all it takes to create a scheduler:

.. literalinclude:: examples/session/example.py
    :language: py


But does it work?
-----------------

The system is tested with over 900 unit tests to 
ensure quality and to deliver what is promised. 
Red Engine is used in production.

Interested?
-----------

There is much more to offer. Read more and try it yourself.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   tutorial/index
   condition_syntax/index
   reference/index
   examples/index



Indices and tables
==================

* :ref:`genindex`

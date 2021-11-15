Welcome to :red:`Red` Engine's documentation!
=============================================

.. image:: https://badgen.net/pypi/v/redengine
   :target: https://pypi.org/project/redengine/

.. image:: https://badgen.net/pypi/python/redengine
   :target: https://pypi.org/project/redengine/

Too lazy to read? :ref:`Get started then. <getting-started>`

Red Engine is an open source Python scheduling library made for 
humans. It is suitable for scrapers, data processes,
process automatization or IOT applications. It also
has minimal dependencies and is pure Python.

Visit the `source code from Github <https://github.com/Miksus/red-engine>`_
or `releases in Pypi page <https://pypi.org/project/redengine/>`_. 


Why :red:`Red` Engine?
----------------------

Red Engine's focus is on productivity: minimizing the 
boiler plate, maximizing readability extendability. 
Creating and scheduling tasks are very easy to do.

:red:`Red` Engine is useful for small to moderate size
projects. It is, however, not meant to handle thousands 
of tasks or execute tasks with the percision required 
by, for example, modern game engines.

Core Features
-------------

- **Easy setup:** Use a premade setup and focus on building your project.
- **Condition parsing:** Scheduling tasks can be done with human readable statements.
- **Parametrization:** Tasks consume session specific or task specific parameters depending on what they need.
- **Extendability:** Almost everything is made for customization. Even the tasks can modify the scheduler.

:red:`Red` Engine has built-in scheduling syntax which
allows logical operations to create complex scheduling logic
with breeze. Also, it very easy to extend and create your 
own conditions.

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
   user_guide/index
   condition_syntax/index
   reference/index
   examples/index



Indices and tables
==================

* :ref:`genindex`

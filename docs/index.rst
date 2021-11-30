
:red:`Red` Engine
=================

.. image:: https://badgen.net/pypi/v/redengine
   :target: https://pypi.org/project/redengine/

.. image:: https://badgen.net/pypi/python/redengine
   :target: https://pypi.org/project/redengine/

Too lazy to read? :ref:`Get started then. <getting-started>`

Red Engine is an open source advanced scheduling library made for 
Python. It is suitable for automating processes, scheduling web scrapers,
and building IOT applications. It also has minimal dependencies 
and is pure Python.

Visit the `source code from Github <https://github.com/Miksus/red-engine>`_
or `releases in Pypi page <https://pypi.org/project/redengine/>`_. 


Why :red:`Red` Engine?
----------------------

Red Engine's focus is on readability, productivity and extendability.
The philosophy behind the library is that simple things should be simple 
and easy and complex things should be done by combining simple things. 
The ultimate focus is in you: the library aims to make your life easier.

:red:`Red` Engine is useful for small to moderate size
projects. It is, however, not meant to handle thousands 
of tasks or execute tasks with the percision required 
by, for example, game engines.

Core Features
-------------

- **Easy setup:** Use a premade setup and focus on building your project.
- **Condition syntax:** Scheduling tasks can be done with human readable statements.
- **Parametrization:** Tasks can be parameterized various ways or they can be pipelined.
- **Extendability:** Almost everything is made for customization. Even the tasks can modify the flow of the system.

:red:`Red` Engine has built-in scheduling syntax which
allows logical operations to create complex scheduling logic
with breeze. Also, it very easy to create your own conditions
for your needs.

Example
-------

This is all it takes to create a scheduler:

.. literalinclude:: examples/session/example.py
    :language: py


But does it work?
-----------------

The system is tested with over 1000 unit tests to 
ensure quality and to deliver what is promised. 
Red Engine is used in production.

Interested?
-----------

There is much more to offer. Start from the 
:ref:`short guide <short-guide>`.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   tutorial/index
   user_guide/index
   condition_syntax/index
   reference/index
   examples/index
   how_it_works
   contributing
   versions


Indices and tables
==================

* :ref:`genindex`

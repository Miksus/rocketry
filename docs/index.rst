
:red:`Red` Engine
=================

.. image:: https://badgen.net/pypi/v/redengine
   :target: https://pypi.org/project/redengine/

.. image:: https://badgen.net/pypi/python/redengine
   :target: https://pypi.org/project/redengine/

Too lazy to read? :ref:`Get started then. <getting-started>`

Red Engine is an advanced open source scheduling library 
with a focus on productivity, readability and extendability. 
It works well in orchestrating task execution in a complex system
or as a tool for quick and simple automation. Example use cases for the 
framework include orchestrating ETL pipelines, scheduling web scrapers
or algorithms, building IOT applications or automating daily tasks.

The library is pure Python with minimal dependencies. It is 
pythonic and the style is similar to other notable frameworks
in Python ecosystem. 

Visit the `source code from Github <https://github.com/Miksus/red-engine>`_
or `releases in Pypi page <https://pypi.org/project/redengine/>`_. 


Why :red:`Red` Engine?
----------------------

Most of the candidates for scheduling framework tend to be 
either complex to configure or too simple for advanced use. Red Engine
aims to handle both sides of the spectrum without sacrificing from the other. 
It only takes a minute to set it up and schedule some tasks but there are 
a lot of advanced features such as parametrization, parallelization, 
pipelining, runtime APIs and logging. The library is also created in mind of
extending and customization.

Red Engine is reliable and well tested. You can build your project
around Red Engine or simply embed it to an existing project. 

Core Features
-------------

- :ref:`Scheduling syntax <scheduling-guide>`: intuitive and very powerful scheduling syntax
- :ref:`Parallelization <parallelizing-guide>`: run tasks simultaneously on separate processes or threads
- :ref:`Parametrization <parametrization-guide>`: parametrize individual tasks and pipeline return values
- :ref:`Extendable <extending-guide>`: almost everything is designed for modifications

Additional Features
-------------------

- :ref:`APIs <api-guide>`: Communicate with your scheduler real time using HTTP requests
- :ref:`Dependencies <dependencies-guide>`: view your task dependencies as a graph
- :ref:`Easy setup <getting-started>`: use the premade configurations and get started immediately.
- :ref:`Logging <logging-guide>`: Red Engine simply extends logging library making task logging trivial
- :ref:`Built-ins <scheduling-guide>`: There are a lot of pre-built conditions for various purposes out of the box

Example
-------

This is all it takes to create a scheduler:

.. literalinclude:: examples/session/example.py
    :language: py

Interested?
-----------

There is much more to offer. See :ref:`quick start <getting-started>`
or :ref:`short guide <short-guide>` to get started with.


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

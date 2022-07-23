
.. meta::
   :description: Rocketry, modern scheduling framework
   :keywords: schedule, task, script, run, Python


.. raw:: html

    <h1 align="center"><a href="https://rocketry.readthedocs.io">Rocketry</a></h1>
    <p align="center">
        <em>The engine to power your Python apps</em>
    </p>
    <p align="center">
        <a href="https://github.com/Miksus/rocketry/actions/workflows/main.yml/badge.svg?branch=master" target="_blank">
            <img src="https://github.com/Miksus/rocketry/actions/workflows/main.yml/badge.svg?branch=master" alt="Test">
        </a>
        <a href="https://codecov.io/gh/Miksus/rocketry" target="_blank">
            <img src="https://codecov.io/gh/Miksus/rocketry/branch/master/graph/badge.svg?token=U2KF1QA5HT" alt="Test coverage">
        </a>
        <a href="https://pypi.org/project/rocketry" target="_blank">
            <img src="https://badgen.net/pypi/v/rocketry?color=969696" alt="Package version">
        </a>
        <a href="https://pypi.org/project/rocketry" target="_blank">
            <img src="https://badgen.net/pypi/python/rocketry?color=969696&labelColor=black" alt="Supported Python versions">
        </a>
    </p>

.. raw:: html

   <hr>

- `Documentation <https://rocketry.readthedocs.io/>`_
- `Source code (Gitbub) <https://github.com/Miksus/rocketry>`_
- `Releases (PyPI) <https://pypi.org/project/rocketry/>`_

No time to read? :ref:`Get started then. <getting-started>`

Rocketry is a modern scheduling framework for Python 
applications. It is simple, clean and extensive.

**Key features:**

- Simple: productive and easy to set up
- Clean: Scheduling is just plain English
- Robust: Well tested and production ready
- Extensive: Has a lot of built-in features
- Customizable: Designed to be modified

**Core functionalities:**

- Powerful scheduling syntax
- A lot of built-in scheduling options
- Task parallelization
- Task parametrization
- Task pipelining
- Modifiable session also in runtime
- Async support

**It looks like this:**

.. literalinclude:: /code/demos/minimal.py
    :language: py

.. raw:: html

   <details>
   <summary><a>Dislike the syntax?</a></summary>

You can also use the condition API instead of the string syntax:

.. literalinclude:: /code/demos/minimal_with_api.py
    :language: py

.. raw:: html

   </details>

Why Rocketry?
---------------

There are a lot of options for scheduler:

- Crontab
- APScheduler
- Airflow

Rocketry provides more features than Crontab and APScheduler
and it is much easier to use than Airflow. Rocketry
has by far the cleanest syntax compared to the alternatives and it is 
the most productive.

Rocketry is the automation backend that sets your applications alive. 
It has customization built into it and it is possible to build really
complex systems that are can self update, self restart and interact with 
users. And all of these are easy to implement.

Here is a demonstration of more advanced case:

.. literalinclude:: /code/demos/intermediate.py
    :language: py


Interested?
-----------

Just install the library:

.. code-block:: console

    pip install rocketry

There is much more to offer. See :ref:`quick start <getting-started>`
and get started with :ref:`tutorials <tutorials>`. There are also 
:ref:`handbooks <handbooks>` to check options and details.


.. toctree::
   :maxdepth: 3
   :caption: Contents:

   tutorial/index
   handbooks/index
   condition_syntax/index
   examples/index
   how_it_works
   contributing
   versions


Indices and tables
==================

* :ref:`genindex`

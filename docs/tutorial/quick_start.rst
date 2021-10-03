.. _getting-started:

Quick start
===========

Install the package from Pip:

.. code-block:: console

    pip install redengine


Generate a quick setup to directory `myproject` that will get you started.

.. code-block:: console

   python -m redengine create myproject

Now you already have a working scheduler system. Just launch it:

.. code-block:: console

   python myproject/main.py

You can also use different :ref:`templates <templates>` depending on the complexity
of your scheduling problem.

What you got?
-------------

The command created you a project directory for your tasks. 
The structure is as follows:

| my_project/
| ├── tasks/
| │ ├── tasks.py
| │ └── ...
| ├── conf.yaml
| └── main.py


You can freely edit the files. In general:

- ``main.py``: Run file this to start the scheduler.
- ``conf.yaml``: Session configuration. See :ref:`conf.yaml <minimal-session>`.
- ``tasks/``: This folder contains your tasks.

  - ``tasks.py``: These file contains tasks. See :ref:`tasks.py <minimal-tasks>`. You can have multiple of these in subdirectories.

What now?
---------

Put your tasks to the ``tasks/`` directory. 

See:

- :ref:`How to set conditions <conditions-intro>` or just :ref:`examples <examples-cond>` for setting the starting conditions (``start_cond``) of the tasks. 
- :ref:`How to parametrize tasks <parametrizing>`.

Red Engine provides you also the batteries so read more to get most 
out of the framework.
.. _getting-started:

Quick start
===========

Install the package from `Pypi <https://pypi.org/project/redengine/>`_:

.. code-block:: console

    pip install redengine


Generate a quick setup to directory `myproject` that will get you started.

.. code-block:: console

   python -m redengine create myproject

Now create your own tasks by creating ``tasks.py`` files to directory 
``my_project/tasks/``, for example:

.. code-block:: python

    from redengine.tasks import FuncTask

    @FuncTask(start_cond="daily after 09:00")
    def wake_up():
        ... # Do whatever

    @FuncTask(start_cond="after task 'wake_up'")
    def have_shower():
        ... # Do whatever

    @FuncTask(start_cond="every 10 minutes")
    def check_messages():
        ... # Do whatever

All done. Just launch the scheduler:

.. code-block:: console

   python myproject/main.py

You can also use different :ref:`templates <templates>` depending on the complexity
of your scheduling problem.

What next?
----------

This is only a small slice what Red Engine has to offer. Read furher 
to explore the features.

See tutorials:

- :ref:`short-guide`
- :ref:`advanced-guide`
- :ref:`All tutorials <tutorials>`

To skip to relevant sections:

- :ref:`Basics of tasks <tasks>`
- :ref:`Basics of conditions <conditions-intro>`
- :ref:`Basics of sessions <session-info>`

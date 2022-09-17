Bigger Applications
===================

When your project grows in size you might want to 
put the application to multiple files. 

.. code-block::

    .
    ├── app
    │   ├── __init__.py
    │   ├── main.py
    │   ├── conditions.py
    │   ├── arguments.py
    │   └── tasks
    │       ├── __init__.py
    │       ├── morning.py
    │       └── evening.py

.. note::

    We use ``__init__.py`` files to make 
    importing easier from the tasks. This 
    structure enables us importing the conditions
    by ``from app.conditions import my_cond``.

Files
-----

Here is a quick explanation of the files and what
you could put in each:

.. glossary::

    ``__init__.py``

        Marks the directory as a package. You can leave 
        these empty.

    ``app/main.py``

        Entry point to the application. This 

        It could look like:

        .. code-block::

            from rocketry import Rocketry
            from app.tasks import morning, evening

            app = Rocketry()

            # Set the task groups
            app.include_group(morning.group)
            app.include_group(evening.group)

            if __name__ == "__main__":
                app.run()

    ``app/tasks/...``

        Put your tasks here. Use also groups and 
        put the groups in the app in ``app/main.py``
        to avoid problems in importing. 

        For example, ``app/tasks/evening.py`` could look like this:

        .. code-block::

            from rocketry import Grouper
            from rocketry.args import FuncArg

            from app.conditions import my_cond
            from app.parameters import get_value

            group = Grouper()

            @group.task(my_cond)
            def do_things(arg=FuncArg(get_value)):
                ...

    ``app/conditions.py``

        Put custom conditions here.

        For example:

        .. code-block::

            from rocketry import Grouper

            group = Grouper()

            @group.cond()
            def my_cond():
                return True or False

        We created a group to conveniently declare 
        the function to be a condition. We don't 
        need to include this group to the app.

    ``app/arguments.py``

        Put custom parameters here. For example:

        .. code-block::

            def get_value():
                return "Hello"

        You can also nest these and pass an argument as 
        to another argument with ``FuncArg`` similarly
        we set in the task.

Running
-------

Then you can run this as a Python module:

.. code-block::

    python -m app.main

.. note::

    You can also turn this to a package using ``setup.py``
    or add CLI by creating ``__main__.py`` file.

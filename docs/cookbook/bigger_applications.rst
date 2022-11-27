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

    ``app/__init__.py``

        Marks the directory as a package. You can leave 
        these empty.

    ``app/main.py``

        Entry point to the application. This 

        It could look like:

        .. code-block::

            from rocketry import Rocketry
            from app.tasks import morning, evening

            app = Rocketry()

            # Set Task Groups
            # ---------------

            app.include_group(morning.group)
            app.include_group(evening.group)

            # Application Setup
            # -----------------

            @app.setup()
            def set_repo(logger=TaskLogger()):
                repo = SQLRepo(engine=create_engine("sqlite:///app.db"), table="tasks", model=MinimalRecord, id_field="created")
                logger.set_repo(repo)

            @app.setup()
            def set_config(config=Config(), env=EnvArg("ENV", default="dev")):
                if env == "prod":
                    config.silence_task_prerun = True
                    config.silence_task_logging = True
                    config.silence_cond_check = True
                else:
                    config.silence_task_prerun = False
                    config.silence_task_logging = False
                    config.silence_cond_check = False
            
            if __name__ == "__main__":
                app.run()

        Read more from :ref:`the app settings cookbook <app-settings-cookbook>`.

    ``app/conditions.py``

        Put your custom conditions here.

        For example:

        .. code-block::

            from rocketry.conds import condition

            @condition()
            def my_cond():
                return True or False

    ``app/arguments.py``

        Put your custom parameters here. For example:

        .. code-block::

            from rocketry.args import argument

            @argument()
            def my_value():
                return "Hello"

        You can also nest these and pass an argument as 
        to another argument with ``FuncArg`` similarly
        we set in the task.

    ``app/tasks/...``

        Put your tasks here. Use also groups and 
        put the groups in the app in ``app/main.py``
        to avoid problems in importing. 

        For example, ``app/tasks/evening.py`` could look like this:

        .. code-block::

            from rocketry import Grouper

            from app.conditions import my_cond
            from app.parameters import my_value

            group = Grouper()

            @group.task(my_cond)
            def do_things(arg=my_value):
                ...

.. note::

    There are various ways to set the tasks.
    You can use other patterns as well.

Running
-------

Then you can run this as a Python module:

.. code-block::

    python -m app.main

Or alternatively create a script that imports and launches the app:

.. code-block:: python

    from app.main import app

    app.run()

.. note::

    You can also turn this to a package using ``setup.py``
    or add CLI by creating ``__main__.py`` file.

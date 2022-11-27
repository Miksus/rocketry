.. _app-settings-cookbook:

App Settings
============

There are various ways to configure your application.
Recommended way is to use the setup hook to 
benefit Rocketry's dynamic arguments.

Here is a simple example to set some configurations:

.. code-block:: python

    from rocketry import Rocketry
    from rocketry.args import Config
    
    app = Rocketry()

    @app.setup()
    def set_config(config=Config()):
        config.silence_task_prerun = True
        config.silence_task_logging = True
        config.silence_cond_check = True

The argument ``config`` will get ``app.session.config``
as the value. This function will run before any tasks 
are run. Therefore it is safe to set the log record repository
or even dynamically create tasks in this function. 

.. note::

    You can split your setup to multiple functions and use
    ``@app.setup()`` multiple times.

Here is a more sophisticated example where we log to an SQL
database and change the configurations based on whether we
are in production or test:

.. code-block:: python

    from redbird.repos import SQLRepo
    from sqlalchemy import create_engine

    from rocketry import Rocketry
    from rocketry.args import TaskLogger, Config, EnvArg, Session
    from rocketry.log import MinimalRecord

    app = Rocketry()

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

You can also modify tasks in the setup. For example,
if you wish to have an environment to test only the
scheduling (without running anything):

.. code-block:: python

    def do_nothing(*args, **kwargs): 
        ...

    @app.setup()
    def set_tasks(session=Session(), env=EnvArg("ENV", default="dev")):
        if env == "test-schedule":
            # Set all tasks to run nothing
            # to test the scheduling works
            for task in session.tasks:
                task.func = do_nothing
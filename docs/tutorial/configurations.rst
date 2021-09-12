Setting up configuration
========================

The configuration of Red Engine can be done 
in various ways but possibly the most convenient
is to configure using ``.yaml`` files. Also the 
tasks can be configured in various ways but 
the most convenient way is to use loaders that
read specific task configuration files.

Configuring the session
-----------------------

The scheduling session can be parsed from an ``.yaml``
file using the function ``redengine.config.parse_yaml``.
This function returns a :class:`redengine.Session` instance.

The ``.yaml`` file is structured in following way:

.. code-block:: yaml

    scheduler: 
        # These are options passed to redengine.Scheduler
        restarting: 'relaunch'

    parameters: 
        # Session specific parameters passed to all tasks as 
        # arguments that require
        env: 'dev'
    
    tasks:
        # Session's tasks and their arguments. It is recommended 
        # to have mainly loaders here.
        - class: YAMLTaskLoader
          path: 'tasks/'
          glob: '**/tasks.yaml' # File pattern of task conf file
          on_startup: True
        - class: YAMLExtensionLoader
          path: 'tasks/'
          glob: '**/extensions.yaml' # File pattern of extension conf file
          on_startup: True

    logging:
        # Logging configurations. The history of each task is 
        # read from a specific types handlers that can also read 
        # the logs. These should also be configured here.
        # This is directly consumed by logging.config.dictConfig.

        handlers:
            memory_handler:
                (): "redengine.log.MemoryHandler"
            
        loggers:
            redengine.task:
                # Put here at least one handler that can also be read.
                handlers: [
                    'memory_handler'
                ]

YAMLTaskLoader is a meta task that loads additional tasks to the session by going 
through all YAML configuration files. By default it looks for all YAML files 
named as ``tasks.yaml``. YAMLExtensionLoader
on the other hand look for files ``extensions.yaml`` and these files configure the 
extensions such as task pipelines.

Example of ``tasks.yaml`` configuraiton:

.. code-block:: yaml

    # Either dict of tasks (key is the name of the task) 
    # or list of tasks 
    my-task-1:
        # PyScript task that executes function 'main'
        # from task-1.py (relative to where conftask.yaml is)
        path: 'task-1.py'
        func: 'main'
    my-task-2:
        path: 'task-2.py'
        func: 'do_stuff'

    
Example of ``extensions.yaml`` configuration:

.. code-block:: yaml

    sequences:
        # These are special built-in extensions that are 
        # useful to create pipelines. 

        # This particular will first execute my-task-1
        # and, when succeeded, will allow my-task-2
        # to execute. It will also run once a day and
        # it will be restarted next day regardless if 
        # it did or did not succeed completely. 
        # Sequences also respect other start
        # conditions and if they are not fulfilled
        # next task on the sequence won't run.
        
        my-pipeline:
            tasks:
                - 'my-task-1'
                - 'my-task-2'
            interval: 
                'time of day between 15:00 and 19:00'

                # Pipeline starts each day at 3 PM and will 
                # execute till 9 PM
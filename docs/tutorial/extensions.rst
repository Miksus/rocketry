Setting extensions
==================

Extensions are additional components that 
change the behaviour of tasks or their 
conditions. Perhaps the most useful components
are task pipelines which forces the given tasks
to execute one after another. Such pipeline is 
the built-in extension :class:`redengine.ext.Sequence`.

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
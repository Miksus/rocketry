.. _config-handbook:

Session Configuration
=====================

There are several configurations options
for the application. 

The configurations can be set by:

.. code-block:: python

    app = Rocketry(config={
        'task_execution': 'process',
        'task_pre_exist': 'raise',
        'force_status_from_logs': True,

        'silence_task_prerun': False,
        'silence_cond_check': False,

        'max_process_count': 5,
        'restarting': 'replace',
        'cycle_sleep': 0.1
    })

This can be later accessed via:

.. code-block::

    >>> app.session.config.task_execution
    'process'

.. note::

    Session config is a Pydantic instance.
    You can also modify this on runtime.

Options
-------

**task_execution**: How tasks are run by default. 

    Options: 

    - process: on separate process (default)
    - thread: on separate thread
    - main: no parallelization

**task_pre_exist**: What happens if a task with given name already exists. 

    Options:

    - ``raise``: An error is thrown (default)
    - ``rename``: the task is renamed (numbers added after the name)
    - ``ignore``: The task is simply not inserted to the session

**force_status_from_logs**: Use logs always to determine the task statuses or times.

    If set as:

    - ``True``: Logs are always read when checking the statuses. Robust but less performant.
    - ``False``: If cached status found, it is used instead. (default)

**silence_task_prerun**: Whether to silence errors occurred before running a task.

    If set as:

    - ``True``: The scheduler does not crash on errors occurred on the startup of a task
    - ``False``: The scheduler crashes. Useful for debug but not for production. (default)
    
**silence_cond_check**: Whether to silence errors occurred when checking conditions' values.

    If set as:

    - ``True``: The scheduler does not crash on errors occurred on checking conditions
    - ``False``: The scheduler crashes. Useful for debug but not for production. (default)

**max_process_count**: Maximum number of processes allowed to be started.

    By default, the number of CPUs.

**restarting**: How the scheduler is restarted (if restart is called).

    Options:

    - ``replace``: Restart by replacing the current process (default)
    - ``relaunch``: Restart by starting a new process
    - ``fresh``: Restart by starting a new process (on new window on Windows)
    - ``recall``: Restart by calling the start method again. Useful for testing the restart

**cycle_sleep**: How long is waited (in seconds) after the scheduler goes through one round of tasks. 

    If ``None``, no sleep and the scheduler is as agressive as it can. If it is too low the 
    system might take a lot of CPU and if too high, the scheduler might not be accurate. 
    
    By default it is set to ``0.1``.

.. _config_instant_shutdown:

**instant_shutdown**: Whether to terminate all tasks on shutdown.

    If set ``False``, the scheduler will wait till all tasks finish on shutdown.
    Running tasks that are past their timeout or their ``end_cond`` are true, 
    are terminated normally. If set ``True``, the scheduler will always 
    terminate all running tasks on shutdown. Shutdown will still wait till all
    threads are finished.
    
    By default, ``False``.

**param_materialize**: When to turn arguments to actual values.

    Whether to turn the arguments to actual values before or after 
    creating threads (for ``execution="thread``) and processes 
    (for ``execution="process``). Options:

    - ``pre``: Before thread/process creation.
    - ``post``: After thread/process creation. (default)

    Only applicable for some argument types and materialization type 
    specified in the argument itself overrides configuration setting.

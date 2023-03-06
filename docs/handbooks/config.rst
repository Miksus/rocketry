.. _config-handbook:

Session Configuration
=====================

There are several configurations options
for the application. 

The configurations can be set by:

.. code-block:: python

    app = Rocketry(
        execution="async",
        task_pre_exist="raise",
        force_status_from_logs=False,
        silence_task_prerun=False,
        silence_task_logging=False,
        silence_cond_check=False,
        max_process_count=5,
        restarting="replace",
        cycle_sleep=0.1
    })

This can be later accessed via:

.. code-block::

    >>> app.session.config.execution
    'process'

.. note::

    Session config is a Pydantic instance.
    You can also modify this on runtime.

Options
-------

**execution**: How tasks are run by default. 

    Options: 

    - ``main``: no parallelization
    - ``async``: run async if can (default in the future)
    - ``thread``: on separate thread
    - ``process``: on separate process (default)

**task_pre_exist**: What happens if a task with given name already exists. 

    Options:

    - ``raise``: An error is thrown (default)
    - ``rename``: the task is renamed (numbers added after the name)
    - ``ignore``: The task is simply not inserted to the session

**force_status_from_logs**: Use logs always to determine the task statuses or times.

    If set as:

    - ``True``: Logs are always read when checking the statuses. Robust but less performant.
    - ``False``: If cached status found, it is used instead. (default)

**silence_task_prerun**: Whether to silence errors occurred during starting up a task.

    If set as:

    - ``True``: The scheduler does not crash on errors occurred on the startup of a task.
    - ``False``: The scheduler crashes. Useful for debug but not for production. (default)
    
    A failure in prerun commonly occurs when there are arguments that cannot be pickled
    or materialized. If task fails in prerun, it cannot simply be run.

**silence_task_logging**: Whether to silence errors occurred during logging a task.

    If set as:

    - ``True``: The scheduler does not crash on errors occurred when logging a task.
    - ``False``: The scheduler crashes. Useful for debug but not for production. (default)

    A failure in task logging commonly occurs if there are connection problems with the 
    logging repository. Failure in logging might be severe as it leads to that Rocketry
    is unable to maintain the history of what tasks ran and when causing some conditions
    to be inaccurate.

**silence_cond_check**: Whether to silence errors occurred when checking conditions' values.

    If set as:

    - ``True``: The scheduler does not crash on errors occurred on checking conditions
    - ``False``: The scheduler crashes. Useful for debug but not for production. (default)

**multilaunch**: Whether to allow parallel runs of the same task.

    In other words, whether to allow a task that is already running to start again.
    By default, ``False``. Session-level option not used if specified to a task.

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

**timezone**: Timezone for scheduling.

    Timezone to be used in evaluating time related condition and 
    displaying datetime. Should be ``datetime.timezone``. 
    One alternative is to use `pytz <https://pythonhosted.org/pytz/>`_.
    
    By default, use system default.

**time_func**: Function for time measurement.

    Function that returns current time in seconds since epoch similar to
    ``time.time()``. Used throughout Rocketry including in condition 
    evaluation and logging. Useful only for testing purposes.
    
    By default, use ``time.time``.

**cls_lock**: Lock class for tasks.

    Lock class used for preventing modifying tasks or checking
    their status elsewhere at the same time. You may override
    this with a custom lock if you need to run multiple instances
    of the same application at the same time. The class should have 
    context manager and methods ``acquire``, ``release`` and ``locked``. 
    By default, ``threading.Lock``.

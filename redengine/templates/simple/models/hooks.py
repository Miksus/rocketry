
from redengine.core import Task, Scheduler

# Task hooks
# ----------

@Task.hook_init
def task_hook_1(task):
    # Run before task init
    ...
    yield
    # Run after task init
    ...

@Task.hook_execute
def task_hook_2(task):
    # Run just before starting executing a task
    ...
    yield
    # Run just after executing a task
    ...

@Task.hook_execute
def task_hook_3(task):
    # You can also process an error if there is any
    ...
    exc_type, exc_value, traceback = yield
    if exc_type is None:
        # The task succeeded
        ...
    else:
        # The task raised an exception
        ...

# Scheduler hooks
# ---------------

@Scheduler.hook_startup
def scheduler_hook_1(scheduler):
    # Run before scheduler startup cycle
    ...
    yield
    # Run after scheduler startup cycle
    ...

@Scheduler.hook_cycle
def scheduler_hook_2(scheduler):
    # Run before scheduler execution cycle
    ...
    yield
    # Run after scheduler execution cycle
    ...

@Scheduler.hook_shutdown
def scheduler_hook_3(scheduler):
    # Run before scheduler shutdown cycle
    ...
    yield
    # Run after scheduler shutdown cycle
    ...

from redengine.core import Task, Scheduler

@Task.hook_init
def env_disable(task:Task):
    """This is run when each task is initiated.
    
    If on dev environment, all tasks not starting
    with 'dev.' are disabled (excluding startup 
    tasks so the loaders work). If not on dev 
    environment, all tasks starting with 'dev.'
    will be disabled."""

    # This section is run before setting the task
    # attributes
    yield
    # Now we have the task attributes

    is_dev_env = task.session.env == "dev"
    is_dev_task = task.name.startswith("dev.")
    is_startup = task.on_startup
    is_shutdown = task.on_shutdown

    if is_dev_task and is_dev_env:
        # Not disabled: running dev task in dev
        pass
    elif not is_dev_env and not is_dev_task:
        # Not disabled: running non dev task in non dev
        pass
    elif is_dev_env and is_startup or is_shutdown:
        # Not disabled: we need loaders also in dev
        pass
    else:
        task.disabled = True

@Scheduler.hook_startup
def startup_hook(scheduler):
    ...

@Scheduler.hook_startup
def startup_hook(scheduler):
    ...
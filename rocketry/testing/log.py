import logging
from rocketry.pybox.time import to_datetime
from rocketry.core import Task

def create_record(
    level,
    pathname="",
    lineno=1,
    name="",
    msg="",
    args=None,
    created=None,
    exc_info=None,
    **kwargs
):
    if created is not None:
        if isinstance(created, str):
            created = to_datetime(created)
        if isinstance(created, float):
            created = int(created)
        if not isinstance(created, int):
            created = int(created.timestamp())

    r = logging.LogRecord(
        level=level,
        exc_info=exc_info,
        # These should not matter:
        name=name,
        pathname=pathname,
        lineno=lineno,
        msg=msg,
        args=args,
        **kwargs
    )
    # Copy-pasted from logging.LogRecord.__init__
    if created is not None:
        r.created = created
        r.msecs = (r.created - int(r.created)) * 1000
        r.relativeCreated = (r.created - logging._startTime) * 1000
    return r

def create_task_record(*args, task_name:str, action:str, **kwargs):
    """Create a task record (for testing)"""
    all_actions = Task._actions
    if action not in all_actions:
        raise ValueError(f"Allowed actions: {all_actions}")
    if 'name' not in kwargs:
        kwargs['name'] = "rocketry.task"

    r = create_record(*args, level=logging.INFO if action != "fail" else logging.ERROR, **kwargs)
    r.task_name = task_name
    r.action = action
    return r

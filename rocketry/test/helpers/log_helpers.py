import sys

from rocketry.pybox.time.convert import to_datetime
from rocketry.testing.log import create_task_record

def log_task_record(task, now, action, start_time=None):
    "Copy of the mechanism of creating an action log"
    if action == "fail":
        try:
            raise RuntimeError("Deliberate failure")
        except Exception:
            exc_info = sys.exc_info()
    else:
        exc_info = None

    msg = {
        "run": "",
        "fail": f"Task '{task.name}' failed",
        "success": "",
    }[action]

    now = to_datetime(now)

    if action == "run":
        start_time = now
    else:
        if start_time is None:
            start_time = task.last_run
        else:
            start_time = to_datetime(start_time)


    record = create_task_record(
        # The content here should not matter for task status
        msg=msg, args=(), exc_info=exc_info,
        created=now, action=action, taask_name=task.name,
    )

    record.start = start_time
    if action != "run":
        record.end = now
        record.runtime = now - start_time
    else:
        task._last_run = start_time

    task.logger.handle(record)
    task._status = action

    setattr(task, f"_last_{action}", now)
    
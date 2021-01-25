
from atlas.core import MultiScheduler, Scheduler
from .tasks import parse_tasks

def parse_scheduler(conf:dict) -> Scheduler:
    """Parse a scheduler section of a config

    Example:
    --------
        {
            "type": "multi",
            "task": [...],
            "maintainer_tasks": [...],
            "restarting": "relaunch",
            ... # Other params to __init__ of Scheduler/Multischeduler
        }
    """
    if conf is None:
        return None
    conf_tasks = conf.pop("tasks", None)
    conf_maintainers = conf.pop("maintainer_tasks", None)
    conf_startup = conf.pop("startup_tasks", None)
    conf_shutdown = conf.pop("shutdown_tasks", None)

    type_ = conf.pop("type", "multi")
    cls = {
        "multi": MultiScheduler,
        "single": Scheduler,
    }[type_]

    conf["tasks"] = parse_tasks(conf_tasks)
    conf["maintainer_tasks"] = parse_tasks(conf_maintainers)
    conf["startup_tasks"] = parse_tasks(conf_startup)
    conf["shutdown_tasks"] = parse_tasks(conf_shutdown)

    return cls(**conf)
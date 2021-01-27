
from atlas.core import MultiScheduler, Scheduler
from atlas.core.task import get_task

from .tasks import parse_tasks, _parse_task

def _parse_scheduler_tasks(conf, resources:dict):
    "Parse a set of tasks for scheduler"
    sequences = resources.get("sequences", {})
    strategies = resources.get("strategies", [])
    if isinstance(conf, list):
        # conf is:
        #   list of tasks (dict or names of tasks)
        tasks = []
        for task in conf:
            if task in sequences:
                # Is list of tasks
                seq_name = task
                task_names = sequences[seq_name]
                tasks += [get_task(task) for task in task_names]

            elif task in strategies:
                # Is list of callables
                strat_name = task
                strategy = strategies[strat_name]
                tasks += strategy()
            elif isinstance(task, str):
                # Is name of a task
                task_name = task
                tasks.append(get_task(task_name))
            else:
                # Is dict {"class": FuncTask, name="..", ...}
                tasks.append(_parse_task(task))
        return tasks
    else:
        # conf is;
        #   dict of tasks ({"task 1": {"class": "FuncTask", ...}})
        return parse_tasks(conf)

def parse_scheduler(conf:dict, resources) -> Scheduler:
    """Parse a scheduler section of a config

    Example:
    --------
        {
            "type": "multi",
            "task": ["task_1", "sequence 1", {"class": "FuncTask", "name": "task 2", ...}],
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

    

    conf["tasks"] = _parse_scheduler_tasks(conf_tasks, resources)
    conf["maintainer_tasks"] = _parse_scheduler_tasks(conf_maintainers, resources)
    conf["startup_tasks"] = _parse_scheduler_tasks(conf_startup, resources)
    conf["shutdown_tasks"] = _parse_scheduler_tasks(conf_shutdown, resources)

    return cls(**conf)
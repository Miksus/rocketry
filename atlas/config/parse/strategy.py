
from atlas.task.maintain import Refresher, ParamRefresher
from ..strategy import TASK_STRATEGIES, TASK_CONFIG_STRATEGIES, PARAM_STRATEGIES
from atlas.conditions import TasksAlive, TaskExecutable
from atlas.time import TimeDelta

import itertools


def _flatten_tasks(funcs):
    materialized = map(lambda x: x(), funcs)
    return list(itertools.chain(*materialized))

def parse_task_config(conf:dict):
    if not conf:
        return {}
    if "class" in conf:
        # Use ConfigFinder
        type_ = conf.pop("class")
        cls = TASK_CONFIG_STRATEGIES[type_]
        return cls(**conf)
    else:
        return StaticConfig(conf)

def parse_task_strategy(conf:dict):
    """Parse a task strategy

    Example:
    --------
        {
            "class": "ProjectFinder",
            "path": "path/to/project",
            # Optional
            "config": {
                "class": "TaskConfigFile",
                "filename": "config.yaml",
            }
        }
    """
    type_ = conf.pop("class")
    task_config = conf.pop("config", None)
    task_config = parse_task_config(task_config)

    # cls is a TaskFinder and config
    cls = TASK_STRATEGIES[type_]
    return cls(**conf, config=task_config)


def parse_strategy(conf:dict, scheduler) -> None:
    """Parse strategy part of the config

    Example:
    --------
        {
            "auto_refresh": True,
            "tasks": [...],       # See parse_task_strategy
            "maintainers": [...], # See parse_task_strategy
        }
    """
    if not conf:
        return

    auto_refresh = conf.pop("auto_refresh", False)

    task_confs = conf.pop("tasks", [])
    maintain_conf = conf.pop("maintainers", [])
    
    task_funcs = [
        parse_task_strategy(task_conf)
        for task_conf in task_confs
    ]
    maintain_funcs = [
        parse_task_strategy(task_conf)
        for task_conf in maintain_conf
    ]

    # Set up tasks 
    if auto_refresh:
        init_tasks = scheduler.tasks.copy()
        init_maintain = scheduler.maintainer_tasks.copy()
        refresh = Refresher(
            get_tasks=lambda: _flatten_tasks(task_funcs) + init_tasks,
            get_maintainers=lambda: _flatten_tasks(maintain_funcs) + init_maintain,
            # Refresher starts when there is no task running
            start_cond=(TasksAlive() == 0) & TaskExecutable(period=TimeDelta("10 seconds"))
        )
        refresh.force_state = True
        scheduler.maintainer_tasks = [refresh]
        scheduler.tasks = []
    else:
        scheduler.tasks.extend(_flatten_tasks(task_funcs))
        scheduler.maintainer_tasks.extend(scheduler.maintainer_tasks)
    return scheduler
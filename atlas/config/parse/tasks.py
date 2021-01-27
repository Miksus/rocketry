
from atlas.core.task import TASK_CLASSES

import importlib

def _parse_task(**conf):
    """Parse a task

    Example:
    --------
        {
            "class": "FuncTask",
            "func": "importing.path.to.func.do_stuff",
            "start_cond": "daily",
            ... # Other params to __init__ of FuncTask
        }
    """
    type_ = conf.pop("class")
    cls = TASK_CLASSES[type_]

    if type_ == "FuncTask":
        # Load the actual function from string
        # (ie. "pkg.mypackage.func" --> from pk.mypackage import func)
        module, func = conf["func"].rsplit('.', 1)
        mdl = importlib.import_module(module)
        conf["func"] = getattr(mdl, func)

    return cls(**conf)


def parse_tasks_from_dict(conf:dict, **kwargs):
    """[summary]
    Example:
    --------
        {
            "task 1": {"class": "FuncTask", ...},

        }
    """
    return [
        _parse_task(**task_conf, name=name)
        for name, task_conf in conf.items()
    ]

def parse_tasks_from_list(conf:list, **kwargs):
    """[summary]
    Example:
    --------
        [
            {"class": "FuncTask", "name": "task 1", ...},
        ]
    """
    return [
        _parse_task(**task_conf)
        for task_conf in conf
    ]

def parse_tasks(conf:dict, **kwargs):
    """Parse a task section of a scheduler

    Example:
    --------
        [
            {
                "class": "FuncTask",
                "func": "importing.path.to.func.do_stuff",
                "start_cond": "daily",
                ... # Other params to __init__ of FuncTask
            }
        ]
    """
    # conf: {"my_task": {"class": "FuncTask", ...}}
    if conf is None:
        return []

    if isinstance(conf, dict):
        return parse_tasks_from_dict(conf)
    elif isinstance(conf, list):
        return parse_tasks_from_list(conf)
    else:
        raise TypeError(type(conf))
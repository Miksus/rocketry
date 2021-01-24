
from atlas.task import FuncTask, ScriptTask

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
    cls = {
        "FuncTask": FuncTask,
        "ScriptTask": ScriptTask,
    }[type_]

    if type_ == "FuncTask":
        # Load the actual function from string
        # (ie. "pkg.mypackage.func" --> from pk.mypackage import func)
        module, func = conf["func"].rsplit('.', 1)
        mdl = importlib.import_module(module)
        conf["func"] = getattr(mdl, func)

    return cls(**conf)

def parse_tasks(conf):
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

    return [
        _parse_task(**setup, name=name)
        for name, setup in conf.items()
    ]
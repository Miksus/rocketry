from atlas.core import BaseCondition, Task

from atlas._session import Session

def _setup_defaults():
    "Set up the task classes and conditions Atlas provides out-of-the-box"
    default_conds = {cls.__name__: cls for cls in BaseCondition.__subclasses__() if not cls.__name__.startswith("_")}
    default_tasks = {cls.__name__: cls for cls in Task.__subclasses__() if not cls.__name__.startswith("_")}

    # Set default list of conds and tasks shared between any Session
    Session.cond_cls = default_conds
    Session.task_cls = default_tasks


from powerbase.core import BaseCondition, Task

from powerbase._session import Session
from powerbase.parse import add_condition_parser
from powerbase.conditions import true, false

def _setup_defaults():
    "Set up the task classes and conditions Powerbase provides out-of-the-box"
    default_conds = {cls.__name__: cls for cls in BaseCondition.__subclasses__() if not cls.__name__.startswith("_")}
    default_tasks = {cls.__name__: cls for cls in Task.__subclasses__() if not cls.__name__.startswith("_")}

    # Set default list of conds and tasks shared between any Session
    Session.cond_cls = default_conds
    Session.task_cls = default_tasks

    # Add some extra parsers from core 
    add_condition_parser({
        "true": true,
        "false": false,
        "always false": false,
        "always true": true
    })

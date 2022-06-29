from redengine.core import BaseCondition, Task
from redengine.core.parameters.parameters import Parameters
from redengine.core.schedule import Scheduler

from redengine.session import Session, Config
from redengine.parse import add_condition_parser
from redengine.parse.session import session_parser
from redengine.conditions import true, false
from redengine.tasks import CommandTask, FuncTask, CodeTask
from redengine.tasks.maintain import ShutDown, Restart
from redengine.tasks.maintain import Restart

def _setup_defaults():
    "Set up the task classes and conditions Redengine provides out-of-the-box"
    
    # Set default list of conds and tasks shared between any Session
    Session._cls_tasks['CommandTask'] = CommandTask
    Session._cls_tasks['CodeTask'] = CodeTask
    Session._cls_tasks['FuncTask'] = FuncTask
    Session._cls_tasks['Restart'] = Restart

    # Add some extra parsers from core 
    add_condition_parser({
        "true": true,
        "false": false,
        "always false": false,
        "always true": true
    })

    Session.parser = session_parser

    # Update type hints
    cls_tasks = (
        Task,
        FuncTask, CommandTask, CodeTask,
        ShutDown, Restart
    )
    for cls_task in cls_tasks:
        cls_task.update_forward_refs(Session=Session, BaseCondition=BaseCondition)

    Config.update_forward_refs(BaseCondition=BaseCondition)
    #Session.update_forward_refs(
    #    Task=Task, Parameters=Parameters, Scheduler=Scheduler
    #)
from rocketry.core import BaseCondition, Task

from rocketry.session import Session, Config
from rocketry.parse import add_condition_parser
from rocketry.conds import true, false
from rocketry.tasks import CommandTask, FuncTask, CodeTask, _DummyTask
from rocketry.tasks.maintain import ShutDown, Restart

from rocketry.conditions.meta import _FuncTaskCondWrapper

def _setup_defaults():
    "Set up the task classes and conditions Rocketry provides out-of-the-box"

    # Add some extra parsers from core
    add_condition_parser({
        "true": true,
        "false": false,
        "always false": false,
        "always true": true
    })

    # Update type hints
    cls_tasks = (
        Task,
        FuncTask, CommandTask, CodeTask,
        ShutDown, Restart, _DummyTask,

        _FuncTaskCondWrapper
    )
    for cls_task in cls_tasks:
        #cls_task.update_forward_refs(Session=Session, BaseCondition=BaseCondition)
        cls_task.model_rebuild(
            force=True,
            _types_namespace={"Session": Session, "BaseCondition": BaseCondition}, 
            _parent_namespace_depth=4
            )

    # Config.update_forward_refs(BaseCondition=BaseCondition)
    Config.model_rebuild(
        force=True, 
        _types_namespace={"Session": Session, "BaseCondition": BaseCondition}, 
        _parent_namespace_depth=4
        )
    #Session.update_forward_refs(
    #    Task=Task, Parameters=Parameters, Scheduler=Scheduler
    #)

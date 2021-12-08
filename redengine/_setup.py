from redengine.core import BaseCondition, Task

from redengine._session import Session
from redengine.parse import add_condition_parser
from redengine.parse.session import session_parser
from redengine.conditions import true, false
from redengine.tasks import CommandTask, FuncTask, CodeTask
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

    # Manually setting extra parsers
    Session.parser["sequences"] = Session._ext_parsers["sequences"]

from .utils import ParserPicker, DictInstanceParser
from .condition import parse_condition
from .utils import _get_session, instances

from redengine.core.task.base import CLS_TASKS
from redengine.tasks import FuncTask

import importlib

def _get_task(*args, session=None, **kwargs):
    "Wrapper of session.get_task to overcome circular import"
    return session.get_task(*args, **kwargs)

def _parse_func_task(**kwargs):

    module, func = kwargs.pop("func").rsplit('.', 1)
    mdl = importlib.import_module(module)
    func = getattr(mdl, func)
    return FuncTask(**kwargs, func=func)

CLS_TASKS["FuncTask"] = _parse_func_task # TODO: Rename this as "Function"

# TODO: Script style to parse_task
parse_task = ParserPicker(
    {
        dict:DictInstanceParser(
            classes=CLS_TASKS, 
            subparsers={
                "start_cond": parse_condition,
                "end_cond": parse_condition,
            },
        ),
        str: _get_task
    }
)

parse_tasks = ParserPicker(
    {
        dict: instances.DictParser(instance_parser=parse_task, key_as_arg="name"),
        list: instances.ListParser(instance_parser=parse_task)
    }
)
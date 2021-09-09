
from .utils import ParserPicker, DictInstanceParser
from .condition import parse_condition
from .utils import _get_session, instances

from redengine.core.task.base import CLS_TASKS
from redengine.tasks import FuncTask, PyScript

import importlib
from pathlib import Path

def _get_task(*args, session=None, **kwargs):
    "Wrapper of session.get_task to overcome circular import"
    return session.get_task(*args, **kwargs)

def _parse_func_task(**kwargs):

    module, func = kwargs.pop("func").rsplit('.', 1)
    mdl = importlib.import_module(module)
    func = getattr(mdl, func)
    return FuncTask(**kwargs, func=func)

def parse_path(path, root=None, **kwargs):
    if isinstance(path, (Path, str)):
        orig_type = type(path)
        path = Path(path)
        if root is not None and not path.is_absolute():
            path = root / path
        path = orig_type(path)
    return path

def get_cls_from_conf(conf:dict, **kwargs):
    filepath = conf.get("path", None)
    if filepath is None:
        name = conf.get("name", None)
        raise KeyError(f"Class of the task '{name}' cannot be determined. Please include 'class' with the configuration.")
    filepath = Path(filepath)
    if filepath.suffix == ".py":
        return PyScript
    else:
        name = conf.get("name", None)
        raise KeyError(f"Class of the task '{name}' cannot be determined for extension {filepath.suffix}. Please include 'class' with the configuration.")

CLS_TASKS["FuncTask"] = _parse_func_task # TODO: Rename this as "Function"

# TODO: Script style to parse_task
parse_task = ParserPicker(
    {
        dict:DictInstanceParser(
            classes=CLS_TASKS, 
            default=get_cls_from_conf,
            subparsers={
                "start_cond": parse_condition,
                "end_cond": parse_condition,
                "path": parse_path,
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
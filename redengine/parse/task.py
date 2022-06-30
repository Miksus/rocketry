
from pathlib import Path

from .utils import ParserPicker, DictInstanceParser
from .condition import parse_condition
from .utils import instances

from redengine.core.task import Task


def _get_task(*args, session=None, **kwargs):
    "Wrapper of session.get_task to overcome circular import"
    return session.get_task(*args, **kwargs)

def parse_path(path, root=None, **kwargs):
    if isinstance(path, (Path, str)):
        orig_type = type(path)
        path = Path(path)
        if root is not None and not path.is_absolute():
            path = root / path
        path = orig_type(path)
    return path

def get_cls_from_conf(conf:dict, **kwargs):
    from redengine.tasks.func import FuncTask
    
    filepath = conf.get("path", None)
    if filepath is None:
        name = conf.get("name", None)
        raise KeyError(f"Class of the task '{name}' cannot be determined. Please include 'class' with the configuration.")
    filepath = Path(filepath)
    if filepath.suffix == ".py":
        return FuncTask
    else:
        name = conf.get("name", None)
        raise KeyError(f"Class of the task '{name}' cannot be determined for extension {filepath.suffix}. Please include 'class' with the configuration.")

# TODO: Script style to parse_task
parse_task = ParserPicker(
    {
        dict:DictInstanceParser(
            classes=lambda: Task.session.cls_tasks, 
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
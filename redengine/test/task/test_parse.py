
from pathlib import Path

import pytest

from redengine.core import Scheduler
from redengine.parse import parse_task
from redengine.tasks import FuncTask, CommandTask

@pytest.mark.parametrize(
    "obj,cls,attrs",
    [
        pytest.param(
            {"class": "FuncTask", "path": "tasks/funcs.py", "func": "myfunc"}, 
            FuncTask,
            {"path": Path("tasks/funcs.py"), "func_name": "myfunc", "name": "a task", "name": "tasks.funcs:myfunc"},
            id="FuncTask without name (delayed)"
        ),
        pytest.param(
            {"class": "FuncTask", "path": "tasks/funcs.py", "func": "myfunc", "name": "a task"}, 
            FuncTask,
            {"path": Path("tasks/funcs.py"), "func_name": "myfunc", "name": "a task"},
            id="FuncTask with name (delayed)"
        ),
        pytest.param(
            {"class": "CommandTask", "command": ["python", "-m", "pip", "list"]}, 
            CommandTask,
            {"action": ["python", "-m", "pip", "list"]},
            id="CommandTask"
        ),
    ]
)
def test_parse_attrs(tmpdir, obj, cls, attrs, session):
    with tmpdir.as_cwd() as old_dir:

        task = parse_task(obj)
        assert isinstance(task, cls)
        for attr, val in attrs.items():
            assert val == getattr(task, attr)

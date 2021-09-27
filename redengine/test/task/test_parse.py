
from pathlib import Path

import pytest

from redengine.core import Scheduler
from redengine.parse import parse_task
from redengine.tasks import FuncTask, PyScript, CommandTask

@pytest.mark.parametrize(
    "obj,cls,attrs",
    [
        pytest.param(
            {"class": "PyScript", "path": "tasks/main.py"}, 
            PyScript,
            {"path": Path("tasks/main.py"), "func": "main", "name": "tasks.main:main"},
            id="PyScript defaults"
        ),
        pytest.param(
            {"class": "PyScript", "path": "tasks/funcs.py", "func": "myfunc"}, 
            PyScript,
            {"path": Path("tasks/funcs.py"), "func": "myfunc", "name": "tasks.funcs:myfunc"},
            id="PyScript simple"
        ),
        pytest.param(
            {"class": "PyScript", "path": "tasks/funcs.py", "func": "myfunc", "name": "a task"}, 
            PyScript,
            {"path": Path("tasks/funcs.py"), "func": "myfunc", "name": "a task"},
            id="PyScript with name"
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

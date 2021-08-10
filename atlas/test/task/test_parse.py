

from atlas.core import Scheduler
from atlas.parse import parse_task
from atlas.task import FuncTask, PyScript

from textwrap import dedent

import sys
import pytest
from pathlib import Path

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
    ]
)
def test_parse_attrs(tmpdir, obj, cls, attrs, session):
    with tmpdir.as_cwd() as old_dir:

        task = parse_task(obj)
        assert isinstance(task, cls)
        for attr, val in attrs.items():
            assert val == getattr(task, attr)

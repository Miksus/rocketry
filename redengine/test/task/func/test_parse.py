
import inspect
from pathlib import Path
import sys
from textwrap import dedent

import pytest

from redengine.tasks.func import FuncTask
from redengine.parse import parse_task


@pytest.fixture()
def task_file(tmpdir):
    sys.path.append(str(tmpdir))
    
    task_dir = tmpdir.mkdir("mypkg") # This should be unique so other test imports won't interfere
    
    script_file = task_dir.join("mytask.py")
    script_file.write(dedent("""
    def do_stuff_1():
        pass
    def do_stuff_2():
        pass
    """))
    task_dir.join("__init__.py").write("")
    with tmpdir.as_cwd() as old_dir:
        yield script_file
    sys.path.remove(str(tmpdir))

@pytest.mark.parametrize("delay", [
    pytest.param(True, id="delay"), pytest.param(False, id="not delay")
])
def test_func_str(session, delay, task_file, tmpdir):
    task = parse_task({"class": "FuncTask", "func_name": "mypkg/mytask.py:do_stuff_1", "delay": delay})
    assert isinstance(task, FuncTask)
    if delay:
        assert task.is_delayed()
        assert task.path == Path("mypkg/mytask.py")
        assert task.func_name == "do_stuff_1"
    else:
        assert not task.is_delayed()
        assert inspect.isfunction(task._func)
        assert task.func.__name__ == "do_stuff_1"


@pytest.mark.parametrize("delay", [
    pytest.param(True, id="delay"), pytest.param(False, id="not delay")
])
def test_with_path(session, delay, task_file, tmpdir):
    task = parse_task({"class": "FuncTask", "func": "do_stuff_1", "path": "mypkg/mytask.py", "delay": delay})
    assert isinstance(task, FuncTask)
    if delay:
        assert task.is_delayed()
        assert task.path == Path("mypkg/mytask.py")
        assert task.func_name == "do_stuff_1"
    else:
        assert not task.is_delayed()
        assert inspect.isfunction(task._func)
        assert task.func.__name__ == "do_stuff_1"
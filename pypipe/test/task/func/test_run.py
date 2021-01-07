
import pytest

from pypipe.core import Scheduler
from pypipe.task import FuncTask
from pypipe.core.task.base import Task, get_task
from pypipe import session

Task.use_instance_naming = True

def run_successful_func():
    print("Running func")

def run_failing_func():
    print("Running func")
    raise RuntimeError("Task failed")

def test_success(tmpdir):
    session.reset()
    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        task = FuncTask(
            run_successful_func, 
        )
        task()
        assert task.status == "success"

def test_failure(tmpdir):
    session.reset()
    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        task = FuncTask(
            run_failing_func, 
        )
        with pytest.raises(RuntimeError):
            task()
        assert task.status == "fail"
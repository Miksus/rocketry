
import pytest

from pypipe import Scheduler, FuncTask
from pypipe.task.base import Task, get_task
from pypipe import reset

Task.use_instance_naming = True

def run_successful_func():
    print("Running func")

def run_failing_func():
    print("Running func")
    raise RuntimeError("Task failed")

def test_success(tmpdir):
    reset()
    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        task = FuncTask(
            run_successful_func, 
            execution="daily",
        )
        task()
        assert task.status == "success"

def test_failure(tmpdir):
    reset()
    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        task = FuncTask(
            run_failing_func, 
            execution="daily", 
        )
        with pytest.raises(RuntimeError):
            task()
        assert task.status == "fail"
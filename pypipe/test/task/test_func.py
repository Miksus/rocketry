
import pytest

from pypipe import Scheduler, FuncTask
from pypipe.task.base import Task

Task.use_instance_naming = True

def run_successful_func():
    print("Running func")

def run_failing_func():
    print("Running func")
    raise RuntimeError("Task failed")

def test_construct(tmpdir):
    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        task = FuncTask(
            run_successful_func, 
            execution="daily",
        )
        assert task.status is None


def test_success(tmpdir):
    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        task = FuncTask(
            run_successful_func, 
            execution="daily",
        )
        task()
        assert task.status == "success"

def test_failure(tmpdir):
    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        task = FuncTask(
            run_failing_func, 
            execution="daily", 
        )
        with pytest.raises(RuntimeError):
            task()
        assert task.status == "fail"

import pytest
import time

from pypipe.core import Scheduler
from pypipe.task import FuncTask
from pypipe.core.task.base import Task, get_task
from pypipe.core.conditions import AlwaysFalse
from pypipe import session

Task.use_instance_naming = True

def run_successful_func():
    print("Running func")

def run_failing_func():
    print("Running func")
    raise RuntimeError("Task failed")

def test_force_run(tmpdir):
    session.reset()
    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        task = FuncTask(
            run_successful_func, 
            name="task",
            start_cond=AlwaysFalse()
        )
        assert not bool(task)
        task.force_run = True
        assert bool(task)
        assert bool(task)
        task()
        assert not task.force_run
        assert not bool(task)


def test_dependency(tmpdir):
    session.reset()
    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        task_a = FuncTask(
            run_successful_func, 
            name="task_a"
        )
        task_b = FuncTask(
            run_successful_func, 
            name="task_b"
        )
        task_dependent = FuncTask(
            run_successful_func, 
            dependent=["task_a", "task_b"],
            name="task_dependent"
        )
        assert not bool(task_dependent)
        task_a()
        assert not bool(task_dependent)
        task_b()
        assert bool(task_dependent)

def test_execution_delta_success(tmpdir):
    session.reset()
    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        task = FuncTask(
            run_successful_func, 
        ).every("2 seconds")

        assert bool(task)
        task()
        assert not bool(task)
        time.sleep(2)
        assert bool(task)

def test_execution_delta_fail(tmpdir):
    session.reset()
    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        task = FuncTask(
            run_failing_func, 
        ).every("2 seconds")

        assert bool(task)
        with pytest.raises(RuntimeError):
            task()
        assert not bool(task)
        time.sleep(2)
        assert bool(task)

        
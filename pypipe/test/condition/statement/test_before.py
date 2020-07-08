
from pypipe.conditions import task_ran, task_failed, task_succeeded

from pypipe import Scheduler, FuncTask
from pypipe.task.base import Task
from pypipe import reset

import time

def run_successful_func():
    print("Running func")

def run_failing_func():
    print("Running func")
    raise RuntimeError("Task failed")

def test_before(tmpdir):
    # Going to tempdir to dump the log files there
    reset()
    with tmpdir.as_cwd() as old_dir:
        task = FuncTask(
            run_successful_func, 
            execution="daily",
        )
        task_parent = FuncTask(
            run_successful_func, 
            execution="daily",
        )
        
        condition = task_ran(task=task).before(task_ran(task=task_parent))
        assert not bool(condition)
        task()
        assert not bool(condition)
        task_parent()
        assert bool(condition)


def test_before_with_period(tmpdir):
    # Going to tempdir to dump the log files there
    reset()
    with tmpdir.as_cwd() as old_dir:
        task = FuncTask(
            run_successful_func, 
            execution="daily",
        )
        task_parent = FuncTask(
            run_successful_func, 
            execution="daily",
        )
        
        condition = task_ran(task=task).before(task_ran(task=task_parent).past("1 seconds"))
        assert not bool(condition)
        task()
        assert not bool(condition)
        task_parent()
        assert bool(condition)

        # Before with period is time dependent
        time.sleep(2)
        assert not bool(condition)
        task_parent()
        assert not bool(condition)
        task()
        assert not bool(condition)
        task_parent()
        assert bool(condition)

def test_after(tmpdir):
    # Going to tempdir to dump the log files there
    reset()
    with tmpdir.as_cwd() as old_dir:
        task = FuncTask(
            run_successful_func, 
            execution="daily",
        )
        task_parent = FuncTask(
            run_successful_func, 
            execution="daily",
        )
        
        condition = task_ran(task=task).after(task_ran(task=task_parent))
        assert not bool(condition)
        task_parent()
        assert not bool(condition)
        task()
        assert bool(condition)

        task_parent()
        assert not bool(condition)
        task()
        task()
        assert bool(condition)


def test_after_with_period(tmpdir):
    # Going to tempdir to dump the log files there
    reset()
    with tmpdir.as_cwd() as old_dir:
        task = FuncTask(
            run_successful_func, 
            execution="daily",
        )
        task_parent = FuncTask(
            run_successful_func, 
            execution="daily",
        )
        
        condition = task_ran(task=task).after(task_ran(task=task_parent).past("1 seconds"))
        assert not bool(condition)
        task_parent()
        assert not bool(condition)
        task()
        assert bool(condition)

        task_parent()
        assert not bool(condition)
        task()
        task()
        assert bool(condition)

        time.sleep(2)
        assert not bool(condition)
        task_parent()
        assert not bool(condition)
        task()
        assert bool(condition)
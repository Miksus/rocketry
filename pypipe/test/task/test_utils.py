
import pytest

from pypipe import Scheduler, FuncTask
from pypipe.task.base import Task, get_task, clear_tasks
from pypipe.task import base

Task.use_instance_naming = True



def run_successful_func():
    print("Running func")

def test_get_task(tmpdir):
    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        task = FuncTask(
            run_successful_func, 
            execution="daily",
            name="example"
        )
        
        t = get_task(task.name)
        assert t is task

def test_clear_task(tmpdir, reset_loggers):
    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        task = FuncTask(
            run_successful_func, 
            execution="daily",
            name="example"
        )
        
        clear_tasks()
        assert base.TASKS == {}
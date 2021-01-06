
import pytest

from pypipe.core import Scheduler
from pypipe.builtin.task import FuncTask
from pypipe.core.task.base import Task, get_task, clear_tasks
from pypipe.core.task import base
from pypipe.core import reset

Task.use_instance_naming = True



def run_successful_func():
    print("Running func")

def test_get_task(tmpdir):
    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        task = FuncTask(
            run_successful_func, 
            name="example"
        )
        
        t = get_task(task.name)
        assert t is task

def test_clear_task(tmpdir):
    reset()
    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        task = FuncTask(
            run_successful_func, 
            name="example"
        )
        
        clear_tasks()
        assert base.TASKS == {}
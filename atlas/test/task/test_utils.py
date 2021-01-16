
import pytest

from atlas.core import Scheduler
from atlas.task import FuncTask
from atlas.core.task.base import Task, get_task, clear_tasks, get_all_tasks
from atlas.core.task import base
from atlas import session

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
    session.reset()
    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        task = FuncTask(
            run_successful_func, 
            name="example"
        )
        assert get_all_tasks() != {}
        clear_tasks()
        assert get_all_tasks() == {}
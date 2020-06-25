
import pytest

from pypipe import Scheduler, FuncTask
from pypipe.task.base import Task, get_task
from pypipe import reset

def test_construct(tmpdir):
    reset()
    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        task = FuncTask(
            lambda : None, 
            execution="daily",
        )
        assert task.status is None

def test_get_task(tmpdir):
    reset()
    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        task = FuncTask(
            lambda : None, 
            execution="daily",
            name="mytask"
        )
        assert get_task("mytask") is task
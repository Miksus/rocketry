
import pytest

from pypipe.core import Scheduler
from pypipe.builtin.task import FuncTask
from pypipe.core.task.base import Task, get_task
from pypipe import session

def test_construct(tmpdir):
    session.reset()
    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        task = FuncTask(
            lambda : None,
        )
        assert task.status is None

def test_get_task(tmpdir):
    session.reset()
    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        task = FuncTask(
            lambda : None, 
            name="mytask"
        )
        assert get_task("mytask") is task

import pytest

from pypipe.core import Scheduler
from pypipe.task import FuncTask
from pypipe.core.task.base import Task, get_task
from pypipe import session

def test_running(tmpdir):
    session.reset()
    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        task = FuncTask(
            lambda : None,
        )
        task.log_running()
        assert "run" == task.status
        assert task.is_running

def test_success(tmpdir):
    session.reset()
    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        task = FuncTask(
            lambda : None,
        )
        task.log_running()
        task.log_success()
        assert "success" == task.status
        assert not task.is_running

def test_fail(tmpdir):
    session.reset()
    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        task = FuncTask(
            lambda : None,
        )
        task.log_running()
        task.log_failure()
        assert "fail" == task.status
        assert not task.is_running
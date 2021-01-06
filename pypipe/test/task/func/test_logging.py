
import pytest

from pypipe.core import Scheduler
from pypipe.builtin.task import FuncTask
from pypipe.core.task.base import Task, get_task
from pypipe.core import reset

def test_running(tmpdir):
    reset()
    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        task = FuncTask(
            lambda : None,
        )
        task.log_running()
        assert "run" == task.status
        assert task.is_running

def test_success(tmpdir):
    reset()
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
    reset()
    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        task = FuncTask(
            lambda : None,
        )
        task.log_running()
        task.log_failure()
        assert "fail" == task.status
        assert not task.is_running
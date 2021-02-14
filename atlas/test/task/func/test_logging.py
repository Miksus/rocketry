import logging
import pytest

from atlas.core import Scheduler
from atlas.task import FuncTask
from atlas.core.task.base import Task, get_task
from atlas import session

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

def test_without_handlers(tmpdir):
    with tmpdir.as_cwd() as old_dir:

        logger = logging.getLogger("atlas.task.test")
        logger.handlers = []
        logger.propagate = False

        task = FuncTask(
            lambda : None, 
            name="task",
            start_cond="always true",
            logger="atlas.task.test"
        )
        task()
        assert task.status is None
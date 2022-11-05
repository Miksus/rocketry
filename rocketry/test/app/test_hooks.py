import asyncio
import logging
import pytest

from redbird.logging import RepoHandler
from redbird.repos import MemoryRepo, CSVFileRepo

from rocketry import Rocketry
from rocketry.conditions.task.task import TaskStarted
from rocketry.args import Return, Arg, FuncArg, Session as SessionArg, TaskLogger, Config
from rocketry.log.log_record import LogRecord, MinimalRecord
from rocketry.tasks import CommandTask
from rocketry.tasks import FuncTask
from rocketry.conds import false, true
from rocketry.core.log import TaskAdapter
from rocketry import Session

def set_logging_defaults():
    task_logger = logging.getLogger("rocketry.task")
    task_logger.handlers = []
    task_logger.setLevel(logging.WARNING)

def test_setup():
    app = Rocketry(execution='async')
    calls = []

    @app.setup()
    def setup_func(logger=TaskLogger(), session=SessionArg(), config=Config()):
        assert isinstance(logger, TaskAdapter)
        assert isinstance(session, Session)
        assert config is session.config

        logger.set_repo(MemoryRepo(model=LogRecord))

        calls.append("setup")

    # Test the setup

    # Make some handlers (these should be deleted)
    task_logger = logging.getLogger("rocketry.task")
    task_logger.addHandler(RepoHandler(MemoryRepo(model=MinimalRecord)))
    task_logger.addHandler(RepoHandler(MemoryRepo(model=MinimalRecord)))

    @app.task(true, on_startup=True)
    def do_things():
        ...
        calls.append("startup task")

    app.session.config.shut_cond = true
    calls.append('starting')
    app.run()
    assert calls == ['starting', 'setup', 'startup task']
    assert len(task_logger.handlers) == 1
    assert task_logger.handlers[0].repo.model == LogRecord
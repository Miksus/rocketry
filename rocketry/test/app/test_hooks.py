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

        calls.append("setup 1")

    app.setup(lambda: calls.append("setup 2"))

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
    assert calls == ['starting', 'setup 1', 'setup 2', 'startup task']
    assert len(task_logger.handlers) == 1
    assert task_logger.handlers[0].repo.model == LogRecord

def test_setup_cache():
    app = Rocketry()
    repo = MemoryRepo(model=MinimalRecord)
    repo.add(MinimalRecord(created=1000, action="run", task_name="do_things"))
    repo.add(MinimalRecord(created=2000, action="success", task_name="do_things"))

    @app.setup()
    def setup_func(logger=TaskLogger()):
        assert task.status is None
        logger.set_repo(repo)
        yield
        assert task.status == "success"

    @app.task()
    def do_things():
        ...
        raise RuntimeError("This should never run")

    # We double check the cache is also set before startup tasks
    @app.task(on_startup=True)
    def verify_cache():
        assert task.status == "success"

    task = app.session[do_things]
    assert task.status is None
    assert task._last_run is None
    assert task._last_success is None
    assert task._last_fail is None
    assert task._last_inaction is None
    assert task._last_crash is None

    app.session.config.shut_cond = true
    app.run()

    # setup should have updated the cache
    assert task.status == "success"
    assert task._last_run == 1000.0
    assert task._last_success == 2000.0

    assert app.session[verify_cache].status == "success"

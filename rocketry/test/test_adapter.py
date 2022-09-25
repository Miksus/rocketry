import logging
from rocketry.core.log import TaskAdapter
import pytest
from redbird.repos import MemoryRepo
from redbird.logging import RepoHandler

def test_warning(session):
    with pytest.warns(UserWarning):
        TaskAdapter(logging.getLogger("rocketry._temp_test"), task="mytask")

def test_equal(session):
    logger = logging.getLogger("rocketry.task")
    assert TaskAdapter(logger, task="mytask") == TaskAdapter(logger, task="mytask")
    assert TaskAdapter(logger, task="mytask") != TaskAdapter(logger, task="another")

    try:
        tmp_logger = logging.getLogger("rocketry._temp_test")
        tmp_logger.addHandler(RepoHandler(MemoryRepo()))
        assert TaskAdapter(tmp_logger, task="mytask") != TaskAdapter(logger, task="mytask")
    finally:
        tmp_logger.handlers = []

def test_add_handler():
    logger = logging.getLogger("rocketry._temp_test")
    try:
        hdlr_repo = RepoHandler(MemoryRepo())
        logger.addHandler(hdlr_repo)

        hdlr = logging.StreamHandler()
        task_logger = TaskAdapter(logger, task="mytask")
        assert task_logger.handlers == [hdlr_repo]
        task_logger.addHandler(hdlr)

        assert task_logger.handlers == [hdlr_repo, hdlr]
        assert logger.handlers == [hdlr_repo, hdlr]
    finally:
        logger.handlers = []
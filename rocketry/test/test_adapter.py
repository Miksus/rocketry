import logging
import pytest
from redbird.logging import RepoHandler
from redbird.repos import MemoryRepo
from rocketry.core.log import TaskAdapter

def test_equal():
    logger = logging.getLogger("rocketry.task")
    try:
        logger.handlers = [RepoHandler(MemoryRepo())]
        assert TaskAdapter(logger, task="mytask") == TaskAdapter(logger, task="mytask")
        assert TaskAdapter(logger, task="mytask") != TaskAdapter(logger, task="another")
        with pytest.warns(UserWarning):
            assert TaskAdapter(logging.getLogger("rocketry._temp_test"), task="mytask") != TaskAdapter(logger, task="mytask")
    finally:
        logger.handlers = []

def test_add_handler():
    logger = logging.getLogger("rocketry._temp_test")
    try:
        hdlr = logging.StreamHandler()
        with pytest.warns(UserWarning):
            task_logger = TaskAdapter(logger, task="mytask")
        assert task_logger.handlers == []
        task_logger.addHandler(hdlr)

        assert task_logger.handlers == [hdlr]
        assert logger.handlers == [hdlr]
    finally:
        logger.handlers = []

import logging
from rocketry.core.log import TaskAdapter

def test_equal():
    logger = logging.getLogger("rocketry.task")
    assert TaskAdapter(logger, task="mytask") == TaskAdapter(logger, task="mytask")
    assert TaskAdapter(logger, task="mytask") != TaskAdapter(logger, task="another")
    assert TaskAdapter(logging.getLogger("rocketry._temp_test"), task="mytask") != TaskAdapter(logger, task="mytask")

def test_add_handler():
    logger = logging.getLogger("rocketry._temp_test")
    try:
        hdlr = logging.StreamHandler()
        task_logger = TaskAdapter(logger, task="mytask")
        assert task_logger.handlers == []
        task_logger.addHandler(hdlr)

        assert task_logger.handlers == [hdlr]
        assert logger.handlers == [hdlr]
    finally:
        logger.handlers = []
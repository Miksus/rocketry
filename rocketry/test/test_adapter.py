import logging
from rocketry.core.log import TaskAdapter

def test_equal():
    logger = logging.getLogger("rocketry.task")
    assert TaskAdapter(logger, task="mytask") == TaskAdapter(logger, task="mytask")
    assert TaskAdapter(logger, task="mytask") != TaskAdapter(logger, task="another")
    assert TaskAdapter(logging.getLogger("rocketry._temp_test"), task="mytask") != TaskAdapter(logger, task="mytask")

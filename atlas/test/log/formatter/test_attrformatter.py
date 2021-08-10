

import pytest

from sys import exc_info
import traceback

from atlas.log import MemoryHandler, AttributeFormatter
import logging
from logging.handlers import QueueHandler
from logging import LogRecord
import multiprocessing

@pytest.mark.parametrize(
    "record,expected",
    [
        pytest.param(
            LogRecord(
                name="atlas.pytest", 
                level=logging.INFO, 
                pathname="C:/path.py", lineno=1, 
                msg="Things are ok",
                args=(), exc_info=None
            ),
            {
                "name": "atlas.pytest",
                "levelname": "INFO",
                "msg": "Things are ok",
                #"exc_text": ""
            },
            id="Info"
        ),
    ]
)
def test_with_queue(record,expected):
    formatter = AttributeFormatter()
    que_handler = QueueHandler(multiprocessing.Queue(-1))

    logger = logging.getLogger("_test.test_queue")
    logger.handlers = []

    # Simulate going through queue
    record = que_handler.prepare(record)
    actual_record = formatter.format(record)

    for exp_key, exp_val in expected.items():
        assert exp_val == getattr(actual_record, exp_key)


@pytest.mark.parametrize(
    "record,expected",
    [
        pytest.param(
            LogRecord(
                name="atlas.pytest", 
                level=logging.ERROR, 
                pathname="C:/path.py", lineno=1, 
                msg="Things are ok",
                args=(), exc_info=None
            ),
            {
                "name": "atlas.pytest",
                "levelname": "ERROR",
                "msg": "Things are ok",
                #"exc_text": ""
            },
            id="Error"
        ),
    ]
)
def test_with_queue_exc(record,expected):
    try:
        raise RuntimeError("Failure")
    except RuntimeError as exc:
        # This is how loggin.Logger._log does it
        record.exc_info = exc_info()
        tb = traceback.format_exc()[:-1] # Ignoring last "\n"

    formatter = AttributeFormatter()
    que_handler = QueueHandler(multiprocessing.Queue(-1))

    logger = logging.getLogger("_test.test_queue")
    logger.handlers = []

    # Simulate going through queue
    record = que_handler.prepare(record)
    actual_record = formatter.format(record)

    for exp_key, exp_val in expected.items():
        assert exp_val == getattr(actual_record, exp_key)
    # Check traceback
    assert tb == actual_record.exc_text
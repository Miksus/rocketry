
import pytest

from powerbase.config import get_default
from powerbase.core.log import TaskAdapter

from powerbase.core import Scheduler
from powerbase.conditions import AlwaysFalse
from powerbase.log import CsvHandler

from textwrap import dedent

import sys
import logging
import datetime
import traceback

@pytest.mark.parametrize(
    "logging_scheme", ['csv_logging', 'memory_logging']
)
def test_logger(tmpdir, logging_scheme):
    with tmpdir.as_cwd() as old_dir:
        get_default(logging_scheme)
        loggers = {name: logging.getLogger(name) for name in logging.root.manager.loggerDict}

        # Some of the powerbase.task handlers must have two way logger (ability to read log file)
        assert any(hasattr(handler, "read") for handler in loggers["powerbase.task"].handlers)

        # Test logging
        task_logger = TaskAdapter(loggers["powerbase.task"], task="mytask")
        task_handler = [handler for handler in loggers["powerbase.task"].handlers if hasattr(handler, "read")][0]

        # Test run
        start = datetime.datetime.now()
        task_logger.info("", extra={"action": "run", "start": start})
        assert {
            #"message": "", 
            "action": "run", 
            "start": start, 
            'task_name': 'mytask'
        }.items() <= task_logger.get_latest().items()

        # Test success
        end = datetime.datetime.now()
        task_logger.info("Task succeeded", extra={"action": "success", "start": start, "end": end, "runtime": end - start})
        
        assert {
            #"message": "Task succeeded", 
            "action": "success", 
            "start": start, 
            "end": end, 
            "runtime": end - start, 
            'task_name': 'mytask'
        }.items() <= task_logger.get_latest().items()

        # Test fail
        end = datetime.datetime.now()
        try:
            raise RuntimeError("Oh...")
        except:
            tb = traceback.format_exc()
            task_logger.exception("Task failed", extra={"action": "fail", "start": start, "end": end, "runtime": end - start})
        
        task_logger
        assert {
            #"message": "Task failed\n" + tb[:-1], 
            "action": "fail", 
            "start": start, 
            "end": end, 
            "runtime": end - start,
            # Traceback
            "exc_text": tb[:-1],
        }.items() <= task_logger.get_latest().items()
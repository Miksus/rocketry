
"""
Test generic logging functionalities of the custom handlers
"""

import multiprocessing, queue, logging, csv
from logging import LogRecord
from sys import exc_info
import pytest

from atlas.log import AttributeFormatter

class FormatterTestBase:

    @pytest.fixture
    def error_record(self):
        try:
            raise RuntimeError("Deliberate failure")
        except:
            rec = LogRecord(
                name="atlas.pytest", 
                level=logging.ERROR, 
                pathname="C:/path.py", lineno=1, 
                msg="a fail log",
                args=(), exc_info=exc_info()
            )
        rec.myextra = "something"
        return rec

    @pytest.fixture
    def info_record(self):
        rec = LogRecord(
            name="atlas.pytest", 
            level=logging.INFO, 
            pathname="C:/path.py", lineno=1, 
            msg="a log",
            args=(), exc_info=None
        )
        rec.myextra = "something"
        return rec

class TestAttributeFormatter(FormatterTestBase):

    @pytest.fixture(scope="function", autouse=True)
    def formatter(self):
        return AttributeFormatter()

    def test_info(self, formatter, info_record):
        record = formatter.format(info_record)
        assert "a log" == record.message
        assert "INFO" == record.levelname
        assert "something" == record.myextra
        assert 1629113147 < record.created
        assert record.exc_text is None

    def test_exception(self, formatter, error_record):
        record = formatter.format(error_record)
        assert "a fail log" == record.message
        assert "ERROR" == record.levelname
        assert "something" == record.myextra
        assert 1629113147 < record.created

        assert record.exc_text.startswith("Traceback (most recent call last):")
        assert record.exc_text.endswith("RuntimeError: Deliberate failure")


"""
Test generic logging functionalities of the custom handlers
"""

import multiprocessing, queue, logging, csv
from logging import LogRecord
from sys import exc_info
import pytest

from powerbase.log import AttributeFormatter

class FormatterTestBase:

    @pytest.fixture
    def error_record(self):
        try:
            raise RuntimeError("Deliberate failure")
        except:
            rec = LogRecord(
                name="powerbase.pytest", 
                level=logging.ERROR, 
                pathname="C:/path.py", lineno=1, 
                msg="a fail log",
                args=(), exc_info=exc_info()
            )
        rec.myextra = "1234"
        rec.excl_extra = "not this"
        return rec

    @pytest.fixture
    def info_record(self):
        rec = LogRecord(
            name="powerbase.pytest", 
            level=logging.INFO, 
            pathname="C:/path.py", lineno=1, 
            msg="a log",
            args=(), exc_info=None
        )
        rec.myextra = "1234"
        rec.excl_extra = "not this"
        return rec

class TestAttributeFormatter(FormatterTestBase):

    @pytest.fixture(scope="function", autouse=True)
    def formatter(self):
        return AttributeFormatter(
            exclude=["excl_extra"], 
            include=["message", "levelname", "myextra", "created", "exc_text"],
            attr_formats={"myextra": int}
        )

    def test_info(self, formatter, info_record):
        record = formatter.format(info_record)
        assert "a log" == record.message
        assert "INFO" == record.levelname
        assert 1234 == record.myextra
        assert 1629113147 < record.created
        assert record.exc_text is None

        assert not hasattr(record, "excl_extra")
        assert not hasattr(record, "lineno")

    def test_exception(self, formatter, error_record):
        record = formatter.format(error_record)
        assert "a fail log" == record.message
        assert "ERROR" == record.levelname
        assert 1234 == record.myextra
        assert 1629113147 < record.created

        assert not hasattr(record, "excl_extra")
        assert not hasattr(record, "lineno")

        assert record.exc_text.startswith("Traceback (most recent call last):")
        assert record.exc_text.endswith("RuntimeError: Deliberate failure")

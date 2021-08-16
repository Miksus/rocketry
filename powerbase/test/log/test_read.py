
"""
Test Powerbase specific reading functionality of the handlers
"""

from _pytest.fixtures import fixture
import pytest
import logging, time
import datetime
from pathlib import Path
from powerbase.log import MemoryHandler, CsvHandler, MongoHandler

class ReadTestBase:
    def test_read(self, logger, handler, tmpdir):
        logger.addHandler(handler)

        epoch_start = time.time()
        logger.info("a log", extra={"action": "run", "task_name": "mytask"})
        epoch_end = time.time()
        
        records = list(handler.read())
        assert 1 == len(records)
        record = records[0]
        assert "run" == record["action"]
        assert "mytask" == record["task_name"]
        assert "a log" == record["msg"]
        assert epoch_start <= float(record["created"]) <= epoch_end

    @pytest.fixture(scope="function")
    def logger(self, request):
        name = __name__ + "." + '.'.join(request.node.nodeid.split("::")[1:])
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        yield logger
        logger.handlers = []

class TestMemory(ReadTestBase):

    @pytest.fixture
    def handler(self):
        return MemoryHandler(store_as="dict")

class TestCsv(ReadTestBase):

    @pytest.fixture
    def handler(self, tmpdir):
        path = Path(str(tmpdir)) / "test_log.csv"
        return CsvHandler(str(path), fields=["created", "task_name", "action", "msg", "exc_text"], delay=True)

class TestMongo(ReadTestBase):

    @pytest.fixture
    def handler(self, collection):
        return MongoHandler(collection)

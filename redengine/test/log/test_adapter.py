
"""
Test TaskAdapter as it is used in Redengine
"""

import pytest
import logging, time
import datetime
from pathlib import Path
from redengine.log import MemoryHandler, CsvHandler, MongoHandler
from redengine.log import AttributeFormatter
from redengine.core.log import TaskAdapter

class AdapterTestBase:
    def test_get_records(self, handler, adapter):

        adapter.logger.addHandler(handler)

        task_start = datetime.datetime(2021, 1, 1)
        task_end = datetime.datetime.now()
        runtime = task_end - task_start

        epoch_start = time.time()
        adapter.info("a log", extra={"action": "success", "start": task_start, "end": task_end, "runtime": runtime})
        epoch_end = time.time()

        start = datetime.datetime.fromtimestamp(epoch_start)
        end = datetime.datetime.fromtimestamp(epoch_end)
        
        records = list(adapter.get_records())
        assert 1 == len(records)
        record = records[0]
        assert "success" == record["action"]
        assert "mytask" == record["task_name"]
        assert "a log" == record["msg"]
        assert epoch_start <= float(record["created"]) <= epoch_end
        assert start <= record["timestamp"] <= end
        assert runtime == record["runtime"]

    def test_get_records_exc(self, handler, adapter, tmpdir):
        adapter.logger.addHandler(handler)

        task_start = datetime.datetime(2021, 1, 1)
        task_end = datetime.datetime.now()
        runtime = task_end - task_start

        epoch_start = time.time()
        try:
            raise RuntimeError("Deliberate failure")
        except:
            adapter.exception("a fail log", extra={"action": "fail", "start": task_start, "end": task_end, "runtime": runtime})

        epoch_end = time.time()

        start = datetime.datetime.fromtimestamp(epoch_start)
        end = datetime.datetime.fromtimestamp(epoch_end)
        
        records = list(adapter.get_records())
        assert 1 == len(records)

        record = records[0]
        assert "fail" == record["action"]
        assert "mytask" == record["task_name"]
        assert "a fail log" == record["msg"]
        assert epoch_start <= float(record["created"]) <= epoch_end
        assert start <= record["timestamp"] <= end
        assert runtime == record["runtime"]

        # Test exception
        assert record["exc_text"].startswith("Traceback (most recent call last):")
        assert record["exc_text"].endswith("RuntimeError: Deliberate failure")

    @pytest.fixture(scope="function")
    def adapter(self, request):
        name = __name__ + "." + '.'.join(request.node.nodeid.split("::")[1:])
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)

        task_logger = TaskAdapter(logger, task="mytask")
        yield task_logger
        task_logger.logger.handlers = []

class TestMemory(AdapterTestBase):

    @pytest.fixture
    def handler(self):
        return MemoryHandler(store_as="dict")

class TestCsv(AdapterTestBase):

    @pytest.fixture
    def handler(self, tmpdir):
        path = Path(str(tmpdir)) / "test_log.csv"
        filename = str(path)
        return CsvHandler(filename, fields=["created", "task_name", "action", "msg", "exc_text", "runtime", "start", "end"])

class TestMongo(AdapterTestBase):

    @pytest.fixture
    def handler(self, collection):
        formatter = AttributeFormatter(attr_formats={"runtime": str})
        handler = MongoHandler(collection)
        handler.setFormatter(formatter)
        return handler


"""
Test TaskAdapter as it is used in Atlas
"""

import pytest
import logging, time
import datetime
from atlas.log import MemoryHandler, CsvHandler
from atlas.core.log import TaskAdapter

@pytest.fixture(scope="function")
def adapter(request):
    name = __name__ + "." + '.'.join(request.node.nodeid.split("::")[1:])
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    task_logger = TaskAdapter(logger, task="mytask")
    yield task_logger
    task_logger.logger.handlers = []

TEST_CASES = [
    pytest.param(lambda: MemoryHandler(store_as="dict"), id="Memory"), 
    pytest.param(lambda: CsvHandler("test_log.csv", fields=["created", "task_name", "action", "msg", "exc_text", "runtime", "start", "end"]), id="CSV"),
]

@pytest.mark.parametrize(
    "cls", TEST_CASES
)
def test_get_records(cls, adapter, tmpdir):
    with tmpdir.as_cwd() as old_dir:
        handler = cls()
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

@pytest.mark.parametrize(
    "cls", TEST_CASES
)
def test_get_records_exc(cls, adapter, tmpdir):
    with tmpdir.as_cwd() as old_dir:
        handler = cls()
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
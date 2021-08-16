
"""
Test Atlas specific reading functionality of the handlers
"""

import pytest
import logging, time
import datetime
from atlas.log import MemoryHandler, CsvHandler

@pytest.fixture(scope="function")
def logger(request):
    name = __name__ + "." + '.'.join(request.node.nodeid.split("::")[1:])
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    yield logger
    logger.handlers = []

@pytest.mark.parametrize(
    "cls", [
        pytest.param(lambda: MemoryHandler(store_as="dict"), id="Memory"), 
        pytest.param(lambda: CsvHandler("test_log.csv", fields=["created", "task_name", "action", "msg", "exc_text"]), id="CSV"),
    ]
)
def test_read(cls, logger, tmpdir):
    with tmpdir.as_cwd() as old_dir:
        handler = cls()
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
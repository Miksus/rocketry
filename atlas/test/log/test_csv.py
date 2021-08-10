
import pytest

from atlas.log import CsvHandler, CsvFormatter
import logging, multiprocessing, traceback, sys
import datetime
from logging.handlers import QueueHandler
from logging import LogRecord

from io import StringIO

def test_read(tmpdir):
    expected_records = [
        {"msg": "event 1", "extra": {"task_name": "mytask", "action": "run"}},
        {"msg": "event 2", "extra": {"task_name": "mytask", "action": "success"}},
    ]
    with tmpdir.as_cwd() as old_dir:
        logger = logging.getLogger("_test.test_types")
        handler = CsvHandler("test.csv", delay=True)
        handler.setFormatter(CsvFormatter(["asctime", "msg", "start_time", "task_name", "action"]))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        for record in expected_records:
            logger.info(**record)

        actual_records = handler.read()
        #actual_records = list(records)
        for actual_record, expected_record in zip(actual_records, expected_records):
            extras = expected_record.pop("extra")

            # Test all basic items found
            assert expected_record.items() <= actual_record.items()

            # Test all extras found
            assert extras.items() <= actual_record.items()

@pytest.mark.parametrize(
    "record,expected,exc",
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
                "levelname": "INFO",
                "msg": "Things are ok",
            },
            None,
            id="Info"
        ),
        pytest.param(
            LogRecord(
                name="atlas.pytest", 
                level=logging.ERROR, 
                pathname="C:/path.py", lineno=1, 
                msg="Things are not ok",
                args=(), exc_info=None
            ),
            {
                "levelname": "ERROR",
                "msg": "Things are not ok",
            },
            RuntimeError("Failure..."),
            id="Error"
        ),
    ]
)
def test_with_queue(record, expected, exc, tmpdir):
    with tmpdir.as_cwd():
        handler = CsvHandler(filename="test.csv")
        handler.setFormatter(CsvFormatter(["message", "levelname", "asctime", "exc_text", "msg", "myextra"]))
        que_handler = QueueHandler(multiprocessing.Queue(-1))

        if exc:
            try:
                raise exc
            except:
                record.exc_info = sys.exc_info()
                tb = traceback.format_exc()[:-1] # Ignoring last "\n"

        logger = logging.getLogger("_test.test_queue")
        logger.handlers = []

        # Simulate going through queue
        record = que_handler.prepare(record)
        handler.handle(record)

        actual_records = list(handler.read())
        assert 1 == len(actual_records)

        actual_record = actual_records[0]
        for exp_key, exp_val in expected.items():
            assert exp_val == actual_record[exp_key]

        # Test traceback
        if exc:
            assert tb == actual_record["exc_text"]
        
        # Test misc
        datetime.datetime.strptime(actual_record["asctime"], '%Y-%m-%d %H:%M:%S,%f')
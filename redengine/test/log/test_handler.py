
"""
Test generic logging functionalities of the custom handlers
"""

import multiprocessing, queue, logging, csv
from sys import exc_info
import sys
import pytest

from redengine.log import QueueHandler, MemoryHandler, CsvHandler, MongoHandler
from redengine.log import AttributeFormatter

class HandlerTestBase:

    @pytest.fixture(scope="function", autouse=True)
    def logger(self, request):
        name = __name__ + '.'.join(request.node.nodeid.split("::")[1:])
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        yield logger
        logger.handlers = []


class TestMemoryhandler(HandlerTestBase):

    @pytest.fixture(scope="function", autouse=True)
    def handler(self, logger):
        handler = MemoryHandler(store_as="record")
        logger.addHandler(handler)
        return handler

    def test_info(self, handler, logger):

        logger.info("a log", extra={"myextra": "something"})
        assert isinstance(handler.records, list)
        assert 1 == len(handler.records)
        
        record = handler.records[0]
        assert "a log" == record.message
        assert "INFO" == record.levelname
        assert "something" == record.myextra
        assert 1629113147 < record.created
        assert record.exc_text is None

    def test_info_with_attr_formatter(self, handler, logger):
        handler.formatter = AttributeFormatter(include=["myextra", "message"])

        logger.info("a log", extra={"myextra": "something", "not_needed": 1})
        assert isinstance(handler.records, list)
        assert 1 == len(handler.records)

        record = handler.records[0]
        assert {"message": "a log", "myextra": "something"} == vars(record)

    def test_exception(self, handler, logger):

        try:
            raise RuntimeError("Deliberate failure")
        except RuntimeError:
            logger.exception("a fail log", extra={"myextra": "something"})

        assert isinstance(handler.records, list)
        assert 1 == len(handler.records)
        
        record = handler.records[0]
        # Test exc_text
        assert record.exc_text.startswith("Traceback (most recent call last):")
        assert record.exc_text.endswith("RuntimeError: Deliberate failure")

        assert "a fail log" == record.message
        assert "ERROR" == record.levelname
        assert "something" == record.myextra
        assert 1629113147 < record.created


class TestCSVhandler(HandlerTestBase):

    @pytest.fixture(scope="function", autouse=True)
    def log_file(self, tmpdir):
        return tmpdir.join("log.csv")

    @pytest.fixture(scope="function", autouse=True)
    def handler(self, log_file, logger):
        handler = CsvHandler(log_file)
        logger.addHandler(handler)
        return handler

    def get_data(self, log_file):
        with open(log_file, "r") as log_file:
            cont = list(csv.reader(log_file))

        headers = cont[0]
        logs = cont[1:]
        return headers, logs

    def test_info(self, tmpdir, handler, logger, log_file):

        logger.info("a log", extra={"myextra": "something"})
        
        headers, logs = self.get_data(log_file)
        assert ['asctime', 'levelname', 'msg', 'exc_text'] == headers

        assert 1 == len(logs)

        record = logs[0]
        level_name = record[1]
        message = record[2]
        exc_text = record[3]

        assert 'INFO' == level_name
        assert 'a log' == message
        assert '' == exc_text

    def test_exception(self, tmpdir, handler, logger, log_file):

        try:
            raise RuntimeError("Deliberate failure")
        except RuntimeError as exc:
            logger.exception("a fail log")
        
        headers, logs = self.get_data(log_file)
        assert ['asctime', 'levelname', 'msg', 'exc_text'] == headers

        assert 1 == len(logs)
        
        record = logs[0]
        level_name = record[1]
        message = record[2]
        exc_text = record[3]

        assert 'ERROR' == level_name
        assert 'a fail log' == message
        assert exc_text.startswith("Traceback (most recent call last):")
        assert exc_text.endswith("RuntimeError: Deliberate failure")


class TestQueueHandler(HandlerTestBase):

#    @pytest.fixture(scope="function", autouse=True)
#    def logger(self, request):
#        name = __name__ + '.'.join(request.node.nodeid.split("::")[1:])
#        logger = logging.getLogger(name)
#        logger.setLevel(logging.INFO)
#        yield logger
#        logger.handlers = []

    @pytest.fixture(scope="function", autouse=True)
    def queue(self):
        return queue.Queue(-1)

    @pytest.fixture(scope="function", autouse=True)
    def handler(self, queue, logger):
        handler = QueueHandler(queue)
        logger.addHandler(handler)
        return handler

    def test_info(self, queue, handler, logger):

        logger.info("a log")

        record = queue.get_nowait()
        assert "a log" == record.msg
        assert 1629113147 < record.created
        assert record.exc_text is None

    def test_exception(self, queue, handler, logger):
        try:
            raise RuntimeError("Deliberate failure")
        except RuntimeError as exc:
            logger.exception("a fail log")
        
        record = queue.get_nowait()
        assert record.exc_text.startswith("Traceback (most recent call last):")
        assert record.exc_text.endswith("RuntimeError: Deliberate failure")

        # Test other
        assert "a fail log" == record.msg
        assert 1629113147 < record.created
        assert "ERROR" == record.levelname

class TestMongoHandler(HandlerTestBase):

#    @pytest.fixture(scope="function", autouse=True)
#    def logger(self, request):
#        name = __name__ + '.'.join(request.node.nodeid.split("::")[1:])
#        logger = logging.getLogger(name)
#        logger.setLevel(logging.INFO)
#        yield logger
#        logger.handlers = []

    def setup_method(self, method):
        """setup any state specific to the execution of the given class (which
        usually contains tests).
        """
        pytest.importorskip("pymongo")

    @pytest.fixture(scope="function")
    def handler(self, collection, logger):
        handler = MongoHandler(collection)
        logger.addHandler(handler)
        return handler

    def test_info(self, collection, handler, logger):

        logger.info("a log")

        record = collection.find_one()
        assert "a log" == record["msg"]
        assert 1629113147 < record["created"]
        assert record["exc_text"] is None

    def test_exception(self, collection, handler, logger):
        try:
            raise RuntimeError("Deliberate failure")
        except RuntimeError as exc:
            logger.exception("a fail log")
        
        record = collection.find_one()
        assert record["exc_text"].startswith("Traceback (most recent call last):")
        assert record["exc_text"].endswith("RuntimeError: Deliberate failure")

        # Test other
        assert "a fail log" == record["msg"]
        assert 1629113147 < record["created"]
        assert "ERROR" == record["levelname"]


import pytest

from pathlib import Path
import os
import sys
import datetime, time
from dateutil.parser import parse as parse_datetime

import atlas
from atlas import Session

from atlas.core.task.base import Task


import logging
from importlib import reload

# Utils
def get_node_id(request):
    components = request.node.nodeid.split("::")
    filename = components[0]
    test_class = components[1] if len(components) == 3 else None
    test_func_with_params = components[-1]
    test_func = test_func_with_params.split('[')[0]

    filename = filename.replace(".py", "").replace("/", "-")
    if test_class:
        return f'{filename}-{test_class}-{test_func_with_params}'
    else:
        return f'{filename}-{test_func_with_params}'

def pytest_sessionstart(session):
    """
    Called after the Session object has been created and
    before performing collection and entering the run test loop.
    """
    atlas.session.debug = True


def copy_file_to_tmpdir(tmpdir, source_file, target_path):
    target_path = Path(target_path)
    source_path = Path(os.path.dirname(__file__)) / "test_files" / source_file

    fh = tmpdir.join(target_path.name)
    with open(source_path) as f:
        fh.write(f.read())
    return fh

@pytest.fixture
def script_files(tmpdir):
    for folder in Path("scripts").parts:
        tmpdir = tmpdir.mkdir(folder)
    
    copy_file_to_tmpdir(tmpdir, source_file="succeeding_script.py", target_path="scripts/succeeding_script.py")
    copy_file_to_tmpdir(tmpdir, source_file="failing_script.py", target_path="scripts/failing_script.py")
    copy_file_to_tmpdir(tmpdir, source_file="parameterized_script.py", target_path="scripts/parameterized_script.py")
    copy_file_to_tmpdir(tmpdir, source_file="parameterized_kwargs_script.py", target_path="scripts/parameterized_kwargs_script.py")


@pytest.fixture(scope="function", autouse=True)
def session():
    session = Session(logging_scheme="memory_logging", config={"debug": True})
    atlas.session = session
    session.set_as_default()
    return session

@pytest.fixture(scope="session", autouse=True)
def set_loggers():
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(action)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    task_logger = logging.getLogger(atlas.session.config["task_logger_basename"])
    task_logger.addHandler(handler)

    yield session

class mockdatetime(datetime.datetime):
    _freezed_datetime = None
    @classmethod
    def now(cls):
        return cls._freezed_datetime

@pytest.fixture
def mock_datetime_now(monkeypatch):
    """Monkey patch datetime.datetime.now
    Returns a function that takes datetime as string as input
    and sets that to datetime.datetime.now()"""
    import datetime
    class mockdatetime(datetime.datetime):
        _freezed_datetime = None
        @classmethod
        def now(cls):
            return cls._freezed_datetime

    def wrapper(dt):
        dt = parse_datetime(dt)
        mockdatetime._freezed_datetime = mockdatetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond)
        monkeypatch.setattr(datetime, 'datetime', mockdatetime)

        # We also need to mock isinstance checks by injecting our
        # class on datetime.datetime on relevant modules
        #datetime.datetime = mockdatetime

    # Getting original datetime.datetime so we can reset it after
    # the test
    
    #_datetime_orig = datetime.datetime

    yield wrapper
    #datetime.datetime = _datetime_orig

@pytest.fixture
def mock_time(monkeypatch):
    """Monkey patch time.time
    Returns a function that takes datetime as string as input
    and sets that to time.time()"""

    def wrapper(dt):
        mocktime = parse_datetime(dt).timestamp()
        monkeypatch.setattr(time, 'time', lambda: mocktime)

    return wrapper

@pytest.fixture
def mock_pydatetime(mock_time, mock_datetime_now):
    """Monkey patch time.time & datetime.datetime.now
    Returns a function that takes datetime as string as input
    and sets that to time.time() and datetime.datetime.now()"""
    
    def wrapper(dt):
        mock_time(dt)
        mock_datetime_now(dt)
    return wrapper


@pytest.fixture(scope="function")
def collection(request):
    pytest.importorskip("pymongo")
    db_name = "pytest"
    col_name = get_node_id(request)
    
    import pymongo
    import yaml
    with open("atlas/test/private.yaml", 'r') as f:
        conf = yaml.load(f)
    conn_str = conf["mongodb"]["conn_str"]
    client = pymongo.MongoClient(conn_str)

    collection = client[db_name][col_name]

    # Empty the collection
    collection.delete_many({})

    yield collection
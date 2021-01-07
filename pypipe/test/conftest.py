
import pytest

from pathlib import Path
import os
import sys

import pypipe

from pypipe.core.task.base import Task


import logging
from importlib import reload


def copy_file_to_tmpdir(tmpdir, filename):
    path = Path(os.path.dirname(__file__)) / "test_files" / filename

    fh = tmpdir.join(filename)
    with open(path) as f:
        fh.write(f.read())
    return path

@pytest.fixture
def successing_script_path(tmpdir):
    return copy_file_to_tmpdir(tmpdir, filename="succeeding_script.py")

@pytest.fixture
def failing_script_path(tmpdir):
    return copy_file_to_tmpdir(tmpdir, filename="failing_script.py")


@pytest.fixture(scope="session", autouse=True)
def reset_loggers():
    #reload(pypipe)
    # prepare something ahead of all tests
    # request.addfinalizer(finalizer_function)

    pypipe.session.reset()
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(action)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    Task.default_logger.addHandler(handler)
    #Task.add_logger_handler(handler)
    yield
    pypipe.session.reset()

    #
import os
import tempfile

import pytest

from atlas.task.api import HTTPConnection
from atlas.task import FuncTask
from atlas import Scheduler, session
from atlas.conditions import IsParameter

from threading import Thread
import requests
import time


@pytest.fixture
def scheduler(tmpdir):
    with tmpdir.as_cwd() as old_dir:
        session.reset()
        #orig_cwd = os.getcwd()
        #tmpdir.chdir()

        session.parameters["shutdown"] = False
        sched = Scheduler(shut_condition=IsParameter(shutdown=True))
        thread = Thread(target=sched)
        thread.start()
        yield sched

        session.parameters["shutdown"] = True
        thread.join()
        #os.chdir(orig_cwd)

@pytest.fixture
def port():
    return 9312 # This probably is not in use

def test_create_api(scheduler):
    # Going to tempdir to dump the log files there
    pass

def test_route_tasks_get(scheduler, port):
    task = HTTPConnection(host="127.0.0.1", port=port, name="http-api")
    task.force_run = True

    FuncTask(lambda: None, name="test-task", parameters={"x": 1, "y":2}, execution="main")
    page = requests.get(f"http://127.0.0.1:{port}/tasks", timeout=1)
    data = page.json()
    assert {"http-api", "test-task"} == set(data.keys())



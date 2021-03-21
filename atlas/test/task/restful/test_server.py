import os
import json
import tempfile

import pytest

from atlas.task.api.http import HTTPConnection
from atlas.task import FuncTask
from atlas import session
from atlas.conditions import IsParameter

from threading import Thread
import requests
import time



@pytest.fixture
def port():
    return 9312 # This probably is not in use

def test_create_api(scheduler):
    # Going to tempdir to dump the log files there
    pass

def test_get(scheduler, port):
    # Test HTTP GET on scheduler running on another thread with a port open
    HTTPConnection(name="http-api", force_run=True)
    session.parameters["http_api"] = {"host": "127.0.0.1", "port": port}

    task = FuncTask(lambda: None, name="test-task", parameters={"x": 1, "y":2}, execution="main", disabled=True)

    # Test tasks
    page = requests.get(f"http://127.0.0.1:{port}/tasks", timeout=1)
    assert page.status_code == 200
    data = page.json()
    assert {"http-api", "test-task"} == set(data.keys())

    # Test logs
    task.log_running()
    task.log_success()
    page = requests.get(f"http://127.0.0.1:{port}/logs/tasks?task_name=test-task", timeout=1)
    assert page.status_code == 200
    data = page.json()

    assert 2 == len(data)

    assert data[0]["action"] == "run"
    assert data[0]["task_name"] == "test-task"

    assert data[1]["action"] == "success"
    assert data[1]["task_name"] == "test-task"

def test_access_tokens(scheduler, port):
    # Test HTTP GET on scheduler running on another thread with a port open
    HTTPConnection(name="http-api", force_run=True)
    session.parameters["http_api"] = {"access_token": "my-password", "host": "127.0.0.1", "port": port}

    # Unauthorized access
    page = requests.get(f"http://127.0.0.1:{port}/ping", timeout=1)
    assert page.status_code == 401
    #assert not page.data

    # Authorized access
    page = requests.get(f"http://127.0.0.1:{port}/ping", timeout=1, headers={"Authorization": "my-password"})
    assert page.status_code == 200


def test_interact(scheduler, port):
    HTTPConnection(name="http-api", force_run=True)
    session.parameters["http_api"] = {"host": "127.0.0.1", "port": port}

    task = FuncTask(lambda: None, name="test-task", parameters={"x": 1, "y":2}, execution="main", disabled=True)

    # Patch force_run
    assert not task.force_run
    assert task.status is None

    data = json.dumps({"force_run": True})
    page = requests.patch(f"http://127.0.0.1:{port}/tasks/test-task", data=data, headers={"content-type": "application/json"}, timeout=1)
    assert page.status_code == 200

    time.sleep(1)
    # Probably should have been run
    assert "success" == task.status 

    # Patch disabled
    assert task.disabled

    data = json.dumps({"disabled": False})
    page = requests.patch(f"http://127.0.0.1:{port}/tasks/test-task", data=data, headers={"content-type": "application/json"}, timeout=1)
    assert page.status_code == 200

    time.sleep(1)
    # Probably should have been run
    assert not task.disabled



def test_wrong_type(scheduler, port):
    HTTPConnection(name="http-api", force_run=True)
    session.parameters["http_api"] = {"access_token": "my-password", "host": "127.0.0.1", "port": port}

    task = FuncTask(lambda: None, name="test-task", parameters={"x": 1, "y":2}, execution="main", disabled=True)

    # Patch force_run
    assert not task.force_run
    assert task.status is None

    page = requests.patch(f"http://127.0.0.1:{port}/tasks/test-task", data="non-json", headers={"content-type": "application/json"}, timeout=1)

    time.sleep(1)
    # Probably should have been run
    assert "success" == task.status 

    # Patch disabled
    assert task.disabled

    data = json.dumps({"disabled": False})
    page = requests.patch(f"http://127.0.0.1:{port}/tasks/test-task", data=data, headers={"content-type": "application/json"}, timeout=1)

    time.sleep(1)
    # Probably should have been run
    assert not task.disabled
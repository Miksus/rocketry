import os
import json
import tempfile
import time
from threading import Thread

import pytest

from redengine.tasks import FuncTask
from redengine.parameters import Parameters, Private

try:
    from redengine.tasks.api.http import HTTPConnection
    import requests
except ImportError:
    # Cannot run these tests
    pass

def test_create_api(scheduler):
    # Going to tempdir to dump the log files there
    pass

def test_get(scheduler, session, api_port):
    # Test HTTP GET on scheduler running on another thread with a port open
    session.config["http_api_host"] = '127.0.0.1'
    session.config["http_api_port"] = api_port # Just a random port
    HTTPConnection(force_run=True)

    # Test session configuration
    session.parameters["myparam"] = "myvalue"

    session.config["configs_private"] = True
    page = requests.get(f"http://127.0.0.1:{api_port}/config", timeout=1)
    assert page.status_code == 403

    session.config["configs_private"] = False
    page = requests.get(f"http://127.0.0.1:{api_port}/config", timeout=1)
    assert page.status_code == 200
    assert {"http_api_host": "127.0.0.1", "http_api_port": api_port}.items() <= page.json().items()

    # Test session params
    session.parameters["myparam"] = "myvalue"
    page = requests.get(f"http://127.0.0.1:{api_port}/parameters", timeout=1)
    assert page.status_code == 200
    data = page.json()
    assert {"myparam": "myvalue"} == data
    
    task = FuncTask(lambda x, y: None, name="test-task", parameters={"x": 1, "y":2}, execution="main", disabled=True)

    # Test tasks
    page = requests.get(f"http://127.0.0.1:{api_port}/tasks", timeout=1)
    assert page.status_code == 200
    data = page.json()
    assert {"HTTP-API", "test-task"} == set(data.keys())

    # Test logs
    task.log_running()
    task.log_success()
    page = requests.get(f"http://127.0.0.1:{api_port}/logs/tasks?task_name=test-task", timeout=1)
    assert page.status_code == 200
    data = page.json()

    assert 2 == len(data)

    assert data[0]["action"] == "run"
    assert data[0]["task_name"] == "test-task"

    assert data[1]["action"] == "success"
    assert data[1]["task_name"] == "test-task"

@pytest.mark.parametrize("from_config", [False, True], ids=["from config", "from params"])
def test_access_tokens(from_config, scheduler, api_port, session):
    # Test HTTP GET on scheduler running on another thread with a port open
    session.config["http_api_host"] = '127.0.0.1'
    session.config["http_api_port"] = api_port # Just a random port

    if from_config:
        session.config["http_api_access_token"] = "my-password"
        HTTPConnection(force_run=True)
    else:
        HTTPConnection(force_run=True, parameters={"access_token": "my-password"})

    # Unauthorized access
    page = requests.get(f"http://127.0.0.1:{api_port}/ping", timeout=1)
    assert page.status_code == 401
    #assert not page.data

    # Authorized access
    page = requests.get(f"http://127.0.0.1:{api_port}/ping", timeout=1, headers={"Authorization": "my-password"})
    assert page.status_code == 200


def test_interact(scheduler, session, api_port):
    session.config["http_api_host"] = '127.0.0.1'
    session.config["http_api_port"] = api_port # Just a random port
    HTTPConnection(force_run=True)

    task = FuncTask(lambda x, y: None, name="test-task", parameters={"x": 1, "y":2}, execution="main", disabled=True)

    # Patch force_run
    assert not task.force_run
    assert task.status is None

    data = json.dumps({"force_run": True})
    page = requests.patch(f"http://127.0.0.1:{api_port}/tasks/test-task", data=data, headers={"content-type": "application/json"}, timeout=1)
    assert page.status_code == 200

    time.sleep(1)
    # Probably should have been run
    assert "success" == task.status 

    # Patch disabled
    assert task.disabled

    data = json.dumps({"disabled": False})
    page = requests.patch(f"http://127.0.0.1:{api_port}/tasks/test-task", data=data, headers={"content-type": "application/json"}, timeout=1)
    assert page.status_code == 200

    time.sleep(1)
    # Probably should have been run
    assert not task.disabled

def test_privatized_host(scheduler, session, api_port):
    # Test HTTP GET on scheduler running on another thread with a port open
    session.config["http_api_host"] = '127.0.0.1'
    session.config["http_api_port"] = api_port # Just a random port
    HTTPConnection(force_run=True)

    task = FuncTask(lambda: None, name="test-task", parameters={"x": 1, "y":2}, execution="main", disabled=True)

    # Test tasks
    page = requests.get(f"http://127.0.0.1:{api_port}/tasks", timeout=1)
    assert page.status_code == 200
    data = page.json()
    assert {"HTTP-API", "test-task"} == set(data.keys())

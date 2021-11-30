import sys
from threading import Thread

import pytest

from redengine import Scheduler
from redengine.conditions import ParamExists

@pytest.fixture
def scheduler(tmpdir, session):
    with tmpdir.as_cwd() as old_dir:
        sched = Scheduler(shut_cond=ParamExists(shutdown=True))
        thread = Thread(target=sched)
        thread.start()
        yield sched

        session.parameters["shutdown"] = True
        thread.join()

@pytest.fixture
def api_port(tmpdir, session):
    pytest.importorskip("flask")
    if sys.platform == "linux" or sys.platform == "linux2":
        pytest.skip("HTTP API not currently supported on Linux")
    return 12700

@pytest.fixture
def api_task(api_port, session):
    pytest.importorskip("flask")
    if sys.platform == "linux" or sys.platform == "linux2":
        pytest.skip("HTTP API not currently supported on Linux")

    from redengine.tasks.api.http import HTTPConnection

    session.config["http_api_host"] = '127.0.0.1'
    session.config["http_api_port"] = api_port # Just a random port
    return HTTPConnection(force_run=True)

@pytest.fixture
def client(tmpdir, api_task):
    pytest.importorskip("flask")
    if sys.platform == "linux" or sys.platform == "linux2":
        pytest.skip("HTTP API not currently supported on Linux")

    app = api_task.create_app()
    app.config['TESTING'] = True

    with tmpdir.as_cwd() as old_cwd:
        with app.test_client() as client:

            yield client


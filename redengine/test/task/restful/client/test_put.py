
import time
import json

import pytest

from redengine.core import Parameters

@pytest.mark.parametrize(
    "existing,query_url,content,expected",
    [
        pytest.param(
            {},
            "/mode",
            "test",
            {"mode": "test"},
            id="String"),
        pytest.param(
            {"param 1": True, "param 2": 2},
            "/mode",
            "test",
            {"mode": "test", "param 1": True, "param 2": 2},
            id="String, have existing params"),
        pytest.param(
            {"mode": "prod"},
            "/mode",
            "test",
            {"mode": "test"},
            id="String, replace"),
        pytest.param(
            {"a param": True},
            "/connections",
            {"sql": "sqlite", "mongodb": "mymongo"},
            {"connections": {"sql": "sqlite", "mongodb": "mymongo"}, "a param": True},
            id="JSON"),
        pytest.param(
            {"a param": True},
            "/server",
            {"connect": True, "priority": 1, "users": ["John", "Jack"], "goups": {"admin": 1, "guest": 2}},
            {"server": {"connect": True, "priority": 1, "users": ["John", "Jack"], "goups": {"admin": 1, "guest": 2}}, "a param": True},
            id="JSON, other types"),
    ],
)
def test_parameters(session, client, existing, query_url, content, expected):
    session.parameters.update(existing)
    assert Parameters(existing).to_dict() == session.parameters.to_dict()
    data = json.dumps(content)
    response = client.put("/parameters" + query_url, data=data, headers={"content-type": "application/json"})
    assert 200 == response.status_code

    assert Parameters(expected).to_dict() == session.parameters.to_dict()


def test_scheduler_shutdown(client, scheduler, session):
    assert session.scheduler.is_alive

    response = client.put("scheduler/shutdown")
    assert response.status_code == 200

    # Wait a bit for the scheduler to shut down
    n_sleeps = 0
    while session.scheduler.is_alive or n_sleeps > 1000:
        time.sleep(0.0001)
        n_sleeps += 1

    assert not session.scheduler.is_alive
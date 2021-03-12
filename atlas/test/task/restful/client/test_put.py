
import tempfile

import pytest

from atlas.task.api import HTTPConnection
from atlas.task import FuncTask
from atlas import Scheduler, session
from atlas.core import Parameters
from atlas.conditions import IsParameter
from atlas.parameters import Private

from threading import Thread
import requests
import time, os, logging
import json

from dateutil.tz import tzlocal

import pandas as pd

# PUT: Update/replace

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
def test_parameters(client, existing, query_url, content, expected):
    session.parameters.update(existing)
    assert Parameters(existing).to_dict() == session.parameters.to_dict()
    data = json.dumps(content)
    response = client.put("/parameters" + query_url, data=data, headers={"content-type": "application/json"})
    assert 200 == response.status_code

    assert Parameters(expected).to_dict() == session.parameters.to_dict()

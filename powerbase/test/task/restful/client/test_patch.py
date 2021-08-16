
import tempfile

import pytest

from powerbase.task.api.http import HTTPConnection
from powerbase.task import FuncTask
from powerbase import Scheduler, session
from powerbase.core import Parameters
from powerbase.parameters import Private

from threading import Thread
import requests
import time, os, logging
import json

from dateutil.tz import tzlocal

import pandas as pd

# PATCH: Update/modify (disallow creation)

@pytest.mark.parametrize(
    "make_tasks,query_url,content,expected_attrs",
    [
        pytest.param(
            lambda: [FuncTask(lambda: None, name="test-task", priority=5)],
            "/test-task",
            {"force_run": True},
            {"test-task": {"force_run": True, "priority": 5, "name": "test-task", "disabled": False}},
            id="Set force run"),
        pytest.param(
            lambda: [FuncTask(lambda: None, name="test-task", priority=5)],
            "/test-task",
            {"disabled": True},
            {"test-task": {"force_run": False, "priority": 5, "name": "test-task", "disabled": True}},
            id="Set disabled"),
        pytest.param(
            lambda: [
                FuncTask(lambda: None, name="test-task", priority=5),
                FuncTask(lambda: None, name="other", priority=3)
            ],
            "/test-task",
            {"disabled": True, "force_run": True},
            {
                "test-task": {"priority": 5, "name": "test-task", "disabled": True, "force_run": True},
                "other": {"priority": 3, "name": "other", "disabled": False, "force_run": False},
            },
            id="Multiple, other task exists"),
    ],
)
def test_tasks(client, make_tasks, query_url, content, expected_attrs):
    make_tasks()
    data = json.dumps(content)
    response = client.patch("/tasks" + query_url, data=data, headers={"content-type": "application/json"})
    assert 200 == response.status_code

    for task_name, task in session.tasks.items():
        for attr, expected in expected_attrs[task_name].items():
            assert expected == getattr(task, attr)



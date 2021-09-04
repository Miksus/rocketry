

from powerbase.core import Parameters
from powerbase.parameters import Private

from powerbase import Scheduler
from powerbase.tasks import FuncTask
from powerbase.conditions import TaskStarted

import pytest

def run_task(secret, public, secret_list, task_secret, task_public):
    assert public == "hello"
    assert secret == "psst"
    assert secret_list == [1, 2, 3]
    assert task_secret == "hsss"
    assert task_public == "world"

def test_parametrization_private(tmpdir, session):
    with tmpdir.as_cwd() as old_dir:

        session.parameters.update({"secret": Private("psst"), "public": "hello", "secret_list": Private([1,2,3])})

        task = FuncTask(run_task, name="a task", execution="main", parameters={"task_secret": Private("hsss"), "task_public": "world"}, force_run=True)
        scheduler = Scheduler(
            shut_condition=TaskStarted(task="a task") >= 1
        )

        scheduler()

        assert "success" == task.status
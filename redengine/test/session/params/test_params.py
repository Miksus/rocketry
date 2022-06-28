
import pytest

from redengine.arguments import Private, Return
from redengine import Scheduler
from redengine.core import parameters
from redengine.tasks import FuncTask
from redengine.conditions import TaskStarted
from redengine.arguments import FuncArg

def run_task(secret, public, secret_list, task_secret, task_public):
    assert public == "hello"
    assert secret == "psst"
    assert secret_list == [1, 2, 3]
    assert task_secret == "hsss"
    assert task_public == "world"

def simple_task_func(value):
    pass

def func_with_return():
    return "x"

def func_with_arg(myparam):
    assert myparam == "x"

def test_parametrization_private(tmpdir, session):
    with tmpdir.as_cwd() as old_dir:

        session.parameters.update({"secret": Private("psst"), "public": "hello", "secret_list": Private([1,2,3])})

        task = FuncTask(run_task, name="a task", execution="main", parameters={"task_secret": Private("hsss"), "task_public": "world"}, force_run=True)
        scheduler = Scheduler(
            shut_cond=TaskStarted(task="a task") >= 1
        )

        scheduler()

        assert "success" == task.status

def test_params_failure(session):
    session.config.silence_task_prerun = True
    @FuncArg.to_session()
    def value():
        raise RuntimeError("Not working")

    task = FuncTask(simple_task_func, name="a task", execution="main", force_run=True)
    scheduler = Scheduler(
        shut_cond=TaskStarted(task="a task") >= 1
    )

    assert task.status is None
    scheduler()

    assert "fail" == task.status

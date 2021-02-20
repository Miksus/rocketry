
import pytest
import time

from atlas.core import Scheduler
from atlas.task import FuncTask
from atlas.core.task.base import Task, get_task
from atlas.core.exceptions import TaskInactionException
from atlas.core.conditions import AlwaysFalse, AlwaysTrue, Any
from atlas import session

Task.use_instance_naming = True


def run_successful_func():
    print("Running func")

def run_failing_func():
    print("Running func")
    raise RuntimeError("Task failed")

def run_inaction():
    raise TaskInactionException()

def run_parametrized(integer, string, optional_float=None):
    assert isinstance(integer, int)
    assert isinstance(string, str)
    assert isinstance(optional_float, float)

@pytest.mark.parametrize(
    "task_func,expected_outcome,exc_cls",
    [
        pytest.param(
            run_successful_func, 
            "success",
            None,
            id="Success"),
        pytest.param(
            run_failing_func, 
            "fail", 
            RuntimeError,
            id="Failure"),
        pytest.param(
            run_inaction, 
            "inaction", 
            None,
            id="Inaction"),
    ],
)
def test_run(tmpdir, task_func, expected_outcome, exc_cls):
    with tmpdir.as_cwd() as old_dir:
        session.reset()
        task = FuncTask(
            task_func, 
            name="a task"
        )

        if exc_cls:
            # Failing task
            with pytest.raises(exc_cls):
                task()
        else:
            # Succeeding task
            task()

        assert task.status == expected_outcome

        df = session.get_task_log()
        records = df[["task_name", "action"]].to_dict(orient="record")
        assert [
            {"task_name": "a task", "action": "run"},
            {"task_name": "a task", "action": expected_outcome},
        ] == records


def test_force_run(tmpdir):
    
    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        session.reset()
        task = FuncTask(
            run_successful_func, 
            name="task",
            start_cond=AlwaysFalse()
        )
        task.force_run = True

        assert bool(task)
        assert bool(task)

        task()
        assert not task.force_run


def test_dependency(tmpdir):

    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        session.reset()
        task_a = FuncTask(
            run_successful_func, 
            name="task_a", 
            start_cond=AlwaysTrue()
        )
        task_b = FuncTask(
            run_successful_func, 
            name="task_b", 
            start_cond=AlwaysTrue()
        )
        task_dependent = FuncTask(
            run_successful_func, 
            dependent=["task_a", "task_b"],
            name="task_dependent", 
            start_cond=AlwaysTrue()
        )
        assert not bool(task_dependent)
        task_a()
        assert not bool(task_dependent)
        task_b()
        assert bool(task_dependent)


# Parametrization
def test_parametrization_runtime(tmpdir):
    with tmpdir.as_cwd() as old_dir:
        session.reset()
        task = FuncTask(
            run_parametrized, 
            name="a task",
        )

        task(integer=1, string="X", optional_float=1.1, extra_parameter="Should not be passed")

        df = session.get_task_log()
        records = df[["task_name", "action"]].to_dict(orient="record")
        assert [
            {"task_name": "a task", "action": "run"},
            {"task_name": "a task", "action": "success"},
        ] == records

def test_parametrization_local(tmpdir):
    with tmpdir.as_cwd() as old_dir:
        session.reset()
        task = FuncTask(
            run_parametrized, 
            name="a task",
            parameters={"integer": 1, "string": "X", "optional_float": 1.1}
        )

        task()

        df = session.get_task_log()
        records = df[["task_name", "action"]].to_dict(orient="record")
        assert [
            {"task_name": "a task", "action": "run"},
            {"task_name": "a task", "action": "success"},
        ] == records
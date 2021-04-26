
import pytest
import time
import multiprocessing

from atlas.core import Scheduler
from atlas.task import FuncTask
from atlas.core.task.base import Task
from atlas.core.exceptions import TaskInactionException
from atlas.core.conditions import AlwaysFalse, AlwaysTrue, Any
from atlas import session

import pandas as pd

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

def run_parametrized_kwargs(**kwargs):
    assert {} != kwargs
    assert isinstance(kwargs["integer"], int)
    assert isinstance(kwargs["string"], str)
    assert isinstance(kwargs["optional_float"], float)

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
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
def test_run(tmpdir, task_func, expected_outcome, exc_cls, execution):

    kwargs = {"log_queue": multiprocessing.Queue(-1)} if execution == "process" else {}
    with tmpdir.as_cwd() as old_dir:
        session.reset()
        task = FuncTask(
            task_func, 
            name="a task",
            execution=execution
        )

        try:
            task(**kwargs)
        except:
            # failing execution="main"
            if expected_outcome != "fail":
                raise

        # Wait for finish
        if execution == "thread":
            times = 0
            timeout = 2
            while task.status != expected_outcome and times < timeout / 0.2:
                time.sleep(0.2)
                times += 1
        elif execution == "process":
            # Do the logging manually
            que = kwargs["log_queue"]
            record = que.get(block=True, timeout=30)
            task.log_record(record)

        assert task.status == expected_outcome

        df = pd.DataFrame(session.get_task_log())
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
            start_cond=AlwaysFalse(),
            execution="main"
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
            start_cond=AlwaysTrue(),
            execution="main"
        )
        task_b = FuncTask(
            run_successful_func, 
            name="task_b", 
            start_cond=AlwaysTrue(),
            execution="main"
        )
        task_dependent = FuncTask(
            run_successful_func, 
            dependent=["task_a", "task_b"],
            name="task_dependent", 
            start_cond=AlwaysTrue(),
            execution="main"
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
            execution="main"
        )

        task(params={"integer": 1, "string": "X", "optional_float": 1.1, "extra_parameter": "Should not be passed"})

        df = pd.DataFrame(session.get_task_log())
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
            parameters={"integer": 1, "string": "X", "optional_float": 1.1},
            execution="main"
        )

        task()

        df = pd.DataFrame(session.get_task_log())
        records = df[["task_name", "action"]].to_dict(orient="record")
        assert [
            {"task_name": "a task", "action": "run"},
            {"task_name": "a task", "action": "success"},
        ] == records

def test_parametrization_kwargs(tmpdir):
    with tmpdir.as_cwd() as old_dir:
        session.reset()
        task = FuncTask(
            run_parametrized_kwargs, 
            name="a task",
            parameters={"integer": 1, "string": "X", "optional_float": 1.1},
            execution="main"
        )

        task()

        df = pd.DataFrame(session.get_task_log())
        records = df[["task_name", "action"]].to_dict(orient="record")
        assert [
            {"task_name": "a task", "action": "run"},
            {"task_name": "a task", "action": "success"},
        ] == records

import pytest
import time

from pypipe.core import Scheduler
from pypipe.task import FuncTask
from pypipe.core.task.base import Task, get_task
from pypipe.core.conditions import AlwaysFalse, AlwaysTrue, Any
from pypipe import session

Task.use_instance_naming = True


def run_successful_func():
    print("Running func")

def run_failing_func():
    print("Running func")
    raise RuntimeError("Task failed")


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
        assert not bool(task)
        task.force_run = True
        assert bool(task)
        assert bool(task)
        task()
        assert not task.force_run
        assert not bool(task)


def test_dependency(tmpdir):

    # Going to tempdir to dump the log files there
    with tmpdir.as_cwd() as old_dir:
        session.reset()
        task_a = FuncTask(
            run_successful_func, 
            name="task_a"
        )
        task_b = FuncTask(
            run_successful_func, 
            name="task_b"
        )
        task_dependent = FuncTask(
            run_successful_func, 
            dependent=["task_a", "task_b"],
            name="task_dependent"
        )
        assert not bool(task_dependent)
        task_a()
        assert not bool(task_dependent)
        task_b()
        assert bool(task_dependent)


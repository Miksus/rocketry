
"""
Tests for methods if one wish to run 
only some parts of the scheduler (like
executing one task)
"""

from atlas.core import Scheduler
from atlas.task import FuncTask
from atlas.time import TimeDelta
from atlas.core.task.base import Task
from atlas.core.exceptions import TaskInactionException
from atlas.conditions import SchedulerCycles, SchedulerStarted, TaskFinished, TaskStarted, AlwaysFalse, AlwaysTrue
from atlas.parameters import Parameters, Private
from atlas import session

import pytest
import pandas as pd

import time


def run_failing():
    raise RuntimeError("Task failed")

def run_succeeding():
    time.sleep(0.05)

def run_inacting():
    raise TaskInactionException()

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
@pytest.mark.parametrize(
    "task_func,run_count,fail_count,success_count",
    [
        pytest.param(
            run_succeeding, 
            1, 0, 1,
            id="Succeeding task"),

        pytest.param(
            run_failing, 
            1, 1, 0,
            id="Failing task"),
        pytest.param(
            run_inacting, 
            1, 0, 0,
            id="Inacting task"),
    ],
)
def test_run_task(tmpdir, execution, task_func, run_count, fail_count, success_count):
    "Example of how to run only one task once using the scheduler"
    with tmpdir.as_cwd() as old_dir:
        session.reset()
        task = FuncTask(task_func, name="task", start_cond=AlwaysFalse(), execution=execution)

        scheduler = Scheduler()
        scheduler.run_task(task)
        scheduler.wait_task_alive()
        scheduler.handle_logs()

        history = pd.DataFrame(task.get_history())
        assert run_count == (history["action"] == "run").sum()
        assert success_count == (history["action"] == "success").sum()
        assert fail_count == (history["action"] == "fail").sum()

"""
Tests for methods if one wish to run
only some parts of the scheduler (like
executing one task)
"""

import asyncio
import time

import pytest

from rocketry.core import Scheduler
from rocketry.tasks import FuncTask
from rocketry.exc import TaskInactionException
from rocketry.conditions import AlwaysFalse

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
def test_run_task(execution, task_func, run_count, fail_count, success_count, session):
    "Example of how to run only one task once using the scheduler"

    task = FuncTask(func=task_func, name="task", start_cond=AlwaysFalse(), execution=execution, session=session)
    logger = task.logger

    scheduler = Scheduler(session=session)
    asyncio.run(scheduler.run_task(task))
    assert run_count == logger.filter_by(action="run").count()

    while scheduler.n_alive > 0:
        time.sleep(0.001)
    scheduler.handle_logs()

    assert success_count == logger.filter_by(action="success").count()
    assert fail_count == logger.filter_by(action="fail").count()

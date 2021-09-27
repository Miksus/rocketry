
"""
Tests for methods if one wish to run 
only some parts of the scheduler (like
executing one task)
"""

import time

import pytest
import pandas as pd

from redengine.core import Scheduler
from redengine.tasks import FuncTask
from redengine.core.exceptions import TaskInactionException
from redengine.conditions import AlwaysFalse

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
def test_run_task(tmpdir, execution, task_func, run_count, fail_count, success_count, session):
    "Example of how to run only one task once using the scheduler"
    with tmpdir.as_cwd() as old_dir:
        
        task = FuncTask(task_func, name="task", start_cond=AlwaysFalse(), execution=execution)

        scheduler = Scheduler()
        scheduler.run_task(task)
        scheduler.wait_task_alive()
        scheduler.handle_logs()

        history = pd.DataFrame(task.logger.get_records())
        assert run_count == (history["action"] == "run").sum()
        assert success_count == (history["action"] == "success").sum()
        assert fail_count == (history["action"] == "fail").sum()
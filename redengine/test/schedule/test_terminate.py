
import time
import os

import pytest
import pandas as pd

from redengine.core import Scheduler
from redengine.tasks import FuncTask
from redengine.core.exceptions import TaskTerminationException
from redengine.conditions import TaskFinished, TaskStarted, AlwaysTrue

def run_slow():
    time.sleep(0.2)
    with open("work.txt", "a") as file:
        file.write("line created\n")

def run_slow_threaded(_thread_terminate_):
    time.sleep(0.2)
    if _thread_terminate_.is_set():
        raise TaskTerminationException
    else:
        with open("work.txt", "a") as file:
            file.write("line created\n")

def get_slow_func(execution):
    return {
        "process": run_slow,
        # Thread tasks are terminated inside the task (the task should respect _thread_terminate_)
        "thread": run_slow_threaded,
    }[execution]

@pytest.mark.parametrize("execution", ["thread", "process"])
def test_without_timeout(tmpdir, execution, session):
    """Test the task.timeout is respected overt scheduler.timeout"""
    # TODO: There is probably better ways to test this
    with tmpdir.as_cwd() as old_dir:

        func_run_slow = get_slow_func(execution)
        task = FuncTask(func_run_slow, name="slow task but passing", start_cond=AlwaysTrue(), timeout="never", execution=execution)

        scheduler = Scheduler(
            shut_cond=TaskFinished(task="slow task but passing") >= 2,
            timeout="0.1 seconds"
        )
        scheduler()

        history = pd.DataFrame(task.logger.get_records())
        # If Scheduler is quick, it may launch the task 3 times 
        # but there still should not be any terminations
        assert 2 <= (history["action"] == "run").sum()
        assert 0 == (history["action"] == "terminate").sum()
        assert 2 <= (history["action"] == "success").sum()
        assert 0 == (history["action"] == "fail").sum()

        assert os.path.exists("work.txt")

@pytest.mark.parametrize("execution", ["thread", "process"])
def test_task_timeout(tmpdir, execution, session):
    """Test task termination due to the task ran too long"""
    with tmpdir.as_cwd() as old_dir:

        func_run_slow = get_slow_func(execution)

        task = FuncTask(func_run_slow, name="slow task", start_cond=AlwaysTrue(), execution=execution)

        scheduler = Scheduler(
            shut_cond=TaskStarted(task="slow task") >= 2,
            timeout="0.1 seconds"
        )
        scheduler()

        history = pd.DataFrame(task.logger.get_records())
        assert 2 == (history["action"] == "run").sum()
        assert 2 == (history["action"] == "terminate").sum()
        assert 0 == (history["action"] == "success").sum()
        assert 0 == (history["action"] == "fail").sum()

        assert not os.path.exists("work.txt")

@pytest.mark.parametrize("execution", ["thread", "process"])
def test_task_terminate(tmpdir, execution, session):
    """Test task termination due to the task was terminated by another task"""

    def terminate_task(_session_):
        _session_.tasks["slow task"].force_termination = True

    with tmpdir.as_cwd() as old_dir:

        func_run_slow = get_slow_func(execution)
        task = FuncTask(func_run_slow, name="slow task", start_cond=AlwaysTrue(), execution=execution)

        FuncTask(terminate_task, name="terminator", start_cond=TaskStarted(task="slow task"), execution="main")
        scheduler = Scheduler(
            shut_cond=TaskStarted(task="slow task") >= 2,
        )
        scheduler()

        history = pd.DataFrame(task.logger.get_records())
        assert 2 == (history["action"] == "run").sum()
        assert 2 == (history["action"] == "terminate").sum()
        assert 0 == (history["action"] == "success").sum()
        assert 0 == (history["action"] == "fail").sum()

        assert not os.path.exists("work.txt")

        # Attr force_termination should be reseted every time the task has been terminated
        assert not task.force_termination


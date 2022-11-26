import asyncio
import datetime
import time
import os

import pytest
from rocketry.conditions.scheduler import SchedulerStarted
from rocketry.conditions.task import TaskRunning

from rocketry.core.time.base import TimeDelta
from rocketry.tasks import FuncTask
from rocketry.exc import TaskTerminationException
from rocketry.conditions import TaskFinished, TaskStarted, AlwaysTrue
from rocketry.args import Session

def run_slow():
    time.sleep(1)
    with open("work.txt", "a", encoding="utf-8") as file:
        file.write("line created\n")

def run_slow_threaded(_thread_terminate_):
    time.sleep(0.2)
    if _thread_terminate_.is_set():
        raise TaskTerminationException
    with open("work.txt", "a", encoding="utf-8") as file:
        file.write("line created\n")

async def run_slow_async():
    await asyncio.sleep(0.2)
    with open("work.txt", "a", encoding="utf-8") as file:
        file.write("line created\n")

def get_slow_func(execution):
    return {
        "async": run_slow_async,
        "process": run_slow,
        # Thread tasks are terminated inside the task (the task should respect _thread_terminate_)
        "thread": run_slow_threaded,
    }[execution]

@pytest.mark.parametrize("execution", ["async", "thread", "process"])
def test_without_timeout(tmpdir, execution, session):
    """Test the task.timeout is respected overt scheduler.timeout"""
    with tmpdir.as_cwd():

        func_run_slow = get_slow_func(execution)
        task = FuncTask(func_run_slow, name="slow task but passing", start_cond=AlwaysTrue(), timeout="never", execution=execution, session=session)

        session.config.shut_cond = (TaskFinished(task="slow task but passing") >= 2) | ~SchedulerStarted(period=TimeDelta("20 seconds"))
        session.config.timeout = 0.1
        session.start()

        logger = task.logger
        # If Scheduler is quick, it may launch the task 3 times
        # but there still should not be any terminations
        assert 2 <= logger.filter_by(action="run").count()
        assert 0 == logger.filter_by(action="terminate").count()
        assert 2 <= logger.filter_by(action="success").count()
        assert 0 == logger.filter_by(action="fail").count()

        assert os.path.exists("work.txt")

@pytest.mark.parametrize("execution", ["async", "thread", "process"])
def test_task_timeout_set_in_session(tmpdir, execution, session):
    """Test task termination due to the task ran too long"""
    with tmpdir.as_cwd():

        func_run_slow = get_slow_func(execution)

        task = FuncTask(func_run_slow, name="slow task", start_cond=AlwaysTrue(), execution=execution, session=session)

        session.config.shut_cond = (TaskStarted(task="slow task") >= 2) | ~SchedulerStarted(period=TimeDelta("20 seconds"))
        session.config.timeout = 0.1
        assert session.config.timeout == datetime.timedelta(milliseconds=100)
        session.start()

        logger = task.logger
        assert 2 == logger.filter_by(action="run").count()
        assert 2 == logger.filter_by(action="terminate").count()
        assert 0 == logger.filter_by(action="success").count()
        assert 0 == logger.filter_by(action="fail").count()

        assert not os.path.exists("work.txt")

@pytest.mark.parametrize("execution", ["async", "thread", "process"])
def test_task_timeout_set_in_task(tmpdir, execution, session):
    """Test task termination due to the task ran too long"""
    with tmpdir.as_cwd():

        func_run_slow = get_slow_func(execution)

        task = FuncTask(func_run_slow, name="slow task", start_cond=AlwaysTrue(), timeout="0.1 sec", execution=execution, session=session)

        session.config.shut_cond = (TaskStarted(task="slow task") >= 2) | ~SchedulerStarted(period=TimeDelta("20 seconds"))
        assert task.timeout == datetime.timedelta(milliseconds=100)
        session.start()

        logger = task.logger
        assert 2 == logger.filter_by(action="run").count()
        assert 2 == logger.filter_by(action="terminate").count()
        assert 0 == logger.filter_by(action="success").count()
        assert 0 == logger.filter_by(action="fail").count()

        assert not os.path.exists("work.txt")

@pytest.mark.parametrize("execution", ["async", "thread", "process"])
def test_task_terminate(tmpdir, execution, session):
    """Test task termination due to the task was terminated by another task"""

    def terminate_task(session=Session()):
        session["slow task"].force_termination = True

    with tmpdir.as_cwd():

        func_run_slow = get_slow_func(execution)
        task = FuncTask(func_run_slow, name="slow task", start_cond=AlwaysTrue(), execution=execution, session=session)

        FuncTask(terminate_task, name="terminator", start_cond=TaskRunning(task=task), execution="main", session=session)
        session.config.shut_cond = (TaskStarted(task="slow task") >= 2) | ~SchedulerStarted(period=TimeDelta("20 seconds"))
        session.start()

        logger = task.logger
        assert 2 == logger.filter_by(action="run").count()
        assert 2 == logger.filter_by(action="terminate").count()
        assert 0 == logger.filter_by(action="success").count()
        assert 0 == logger.filter_by(action="fail").count()

        assert not os.path.exists("work.txt")

        # Attr force_termination should be reseted every time the task has been terminated
        assert not task.force_termination


@pytest.mark.parametrize("execution", ["async", "thread", "process"])
def test_task_terminate_end_cond(tmpdir, execution, session):
    """Test task termination due to the task ran too long"""
    #! NOTE: CI observed to get stuck in this for some times
    with tmpdir.as_cwd():

        func_run_slow = get_slow_func(execution)

        task = FuncTask(func_run_slow, name="slow task", start_cond=AlwaysTrue(), end_cond=TaskStarted(task='slow task'), execution=execution, session=session)

        session.config.shut_cond = (TaskStarted(task="slow task") >= 1) | ~SchedulerStarted(period=TimeDelta("20 seconds"))
        session.start()

        logger = task.logger
        assert 1 == logger.filter_by(action="run").count()
        assert 1 == logger.filter_by(action="terminate").count()
        assert 0 == logger.filter_by(action="success").count()
        assert 0 == logger.filter_by(action="fail").count()

        assert not os.path.exists("work.txt")

@pytest.mark.parametrize("execution", ["async", "thread", "process"])
def test_permanent_task(tmpdir, execution, session):
    """Test the task.timeout is respected overt scheduler.timeout"""
    with tmpdir.as_cwd():

        func_run_slow = get_slow_func(execution)
        task = FuncTask(func_run_slow, name="slow task but passing", start_cond=AlwaysTrue(), timeout="1 ms", permanent=True, execution=execution, session=session)

        session.config.shut_cond = (TaskStarted(task="slow task but passing") >= 3) | ~SchedulerStarted(period=TimeDelta("20 seconds"))
        session.config.timeout = 0.1
        session.start()

        logger = task.logger
        # If Scheduler is quick, it may launch the task 3 times
        # but there still should not be any terminations
        assert 3 <= logger.filter_by(action="run").count()
        assert 1 == logger.filter_by(action="terminate").count() # The last run is terminated
        assert 2 == logger.filter_by(action="success").count()
        assert 0 == logger.filter_by(action="fail").count()

        assert logger.filter_by(action="terminate").last().created >= logger.filter_by(action="success").last().created

        assert os.path.exists("work.txt")

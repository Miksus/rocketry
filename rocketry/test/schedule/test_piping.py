
import logging
import time

import pytest
from rocketry.conditions.scheduler import SchedulerStarted
from rocketry.core.time.base import TimeDelta

from rocketry.tasks import FuncTask
from rocketry.conditions import TaskStarted, DependSuccess

def run_failing():
    raise RuntimeError("Task failed")

def run_succeeding():
    pass

def run_slow():
    time.sleep(30)

def create_line_to_file():
    with open("work.txt", "a", encoding="utf-8") as file:
        file.write("line created\n")

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_dependent(tmpdir, execution, session):
    with tmpdir.as_cwd():

        # Running the master tasks only once
        task_a = FuncTask(run_succeeding, name="A", start_cond=~TaskStarted(), execution=execution, session=session)
        task_b = FuncTask(run_succeeding, name="B", start_cond=~TaskStarted(), execution=execution, session=session)

        task_after_a = FuncTask(
            run_succeeding,
            name="After A",
            start_cond=DependSuccess(depend_task="A"),
            execution=execution,
            session=session
        )
        task_after_b = FuncTask(
            run_succeeding,
            name="After B",
            start_cond=DependSuccess(depend_task="B"),
            execution=execution,
            session=session
        )
        task_after_all = FuncTask(
            run_succeeding,
            name="After all",
            start_cond=DependSuccess(depend_task="After A") & DependSuccess(depend_task="After B"),
            execution=execution,
            session=session
        )

        session.config.shut_cond = (TaskStarted(task="After all") >= 1) | ~SchedulerStarted(period=TimeDelta("10 seconds"))
        session.start()

        repo = logging.getLogger(session.config.task_logger_basename).handlers[0].repo

        a_start = repo.filter_by(task_name="A", action="run").first().created
        b_start = repo.filter_by(task_name="B", action="run").first().created
        after_a_start = repo.filter_by(task_name="After A", action="run").first().created
        after_b_start = repo.filter_by(task_name="After B", action="run").first().created
        after_all_start = repo.filter_by(task_name="After all", action="run").first().created

        assert a_start < after_a_start < after_all_start
        assert b_start < after_b_start < after_all_start

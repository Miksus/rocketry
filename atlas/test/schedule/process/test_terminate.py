
from atlas.core import Scheduler
from atlas.task import FuncTask
from atlas.time import TimeDelta
from atlas.core.task.base import Task
from atlas.conditions import SchedulerCycles, SchedulerStarted, TaskFinished, TaskStarted, AlwaysFalse, AlwaysTrue

import pandas as pd
import pytest

import logging
import sys
import time
import os
import multiprocessing


def run_slow():
    time.sleep(0.2)
    with open("work.txt", "a") as file:
        file.write("line created\n")

def test_without_timeout(tmpdir, session):
    with tmpdir.as_cwd() as old_dir:

        task = FuncTask(run_slow, name="slow task but passing", start_cond=AlwaysTrue(), timeout="never")

        scheduler = Scheduler(
            shut_condition=(TaskFinished(task="slow task but passing") >= 2) | ~SchedulerStarted(period=TimeDelta("5 second")),
            timeout="0.1 seconds"
        )
        scheduler()

        # NOTE: Actual number of runs may depend on how busy the process has been
        # (in case: runs == 1 --> no shutdown, continue --> check logs --> runs now 2 --> run task --> shutdown --> runs now 3)
        # thus we accept more than two runs  
        history = pd.DataFrame(task.get_history())
        assert 2 <= (history["action"] == "run").sum()
        assert 0 == (history["action"] == "terminate").sum()
        assert 2 <= (history["action"] == "success").sum()
        assert 0 == (history["action"] == "fail").sum()

        assert os.path.exists("work.txt")

def test_task_timeout(tmpdir, session):
    with tmpdir.as_cwd() as old_dir:

        task = FuncTask(run_slow, name="slow task", start_cond=AlwaysTrue(), execution="process")

        scheduler = Scheduler(
            shut_condition=(TaskStarted(task="slow task") >= 2) | ~SchedulerStarted(period=TimeDelta("5 second")),
            timeout="0.1 seconds"
        )
        scheduler()

        history = pd.DataFrame(task.get_history())
        assert 2 == (history["action"] == "run").sum()
        assert 2 == (history["action"] == "terminate").sum()
        assert 0 == (history["action"] == "success").sum()
        assert 0 == (history["action"] == "fail").sum()

        assert not os.path.exists("work.txt")

def test_task_terminate(tmpdir, session):
    def terminate_task(_scheduler_):
        _scheduler_.tasks[0].force_termination = True
    with tmpdir.as_cwd() as old_dir:

        task = FuncTask(run_slow, name="slow task", start_cond=AlwaysTrue(), execution="process")
        FuncTask(terminate_task, name="terminator", start_cond=TaskStarted(task="slow task"), execution="main"),
        scheduler = Scheduler(
            shut_condition=(TaskStarted(task="slow task") >= 2) | ~SchedulerStarted(period=TimeDelta("5 second")),
        )
        scheduler()

        history = pd.DataFrame(task.get_history())
        assert 2 == (history["action"] == "run").sum()
        assert 2 == (history["action"] == "terminate").sum()
        assert 0 == (history["action"] == "success").sum()
        assert 0 == (history["action"] == "fail").sum()

        assert not os.path.exists("work.txt")

        # Attr force_termination should be reseted every time the task has been terminated
        assert not task.force_termination


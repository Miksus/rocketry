
from powerbase.core import Scheduler
from powerbase.tasks import FuncTask
from powerbase.time import TimeDelta
from powerbase.core.task.base import Task
from powerbase.core.exceptions import TaskInactionException
from powerbase.conditions import SchedulerCycles, SchedulerStarted, TaskFinished, TaskStarted, AlwaysFalse, AlwaysTrue

import pandas as pd
import pytest

import logging
import sys
import time
import os
import multiprocessing

def run_succeeding():
    pass

def run_creating_child():

    proc = multiprocessing.Process(target=run_succeeding, daemon=True)
    proc.start()

def test_creating_child(tmpdir, session):
    with tmpdir.as_cwd() as old_dir:

        # To be confident the scheduler won't lie to us
        # we test the task execution with a job that has
        # actual measurable impact outside powerbase
        FuncTask(run_creating_child, name="task_1", start_cond=AlwaysTrue())
        scheduler = Scheduler(
            shut_condition=(TaskStarted(task="task_1") >= 1) | ~SchedulerStarted(period=TimeDelta("1 second")),
            tasks_as_daemon=False
        )

        scheduler()

        history = pd.DataFrame(session.get_task("task_1").get_history())
        assert 1 == (history["action"] == "run").sum()
        assert 1 == (history["action"] == "success").sum()
        assert 0 == (history["action"] == "fail").sum()

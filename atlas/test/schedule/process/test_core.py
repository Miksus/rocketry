
from atlas.core import Scheduler
from atlas.task import FuncTask
from atlas.time import TimeDelta
from atlas.core.task.base import Task, clear_tasks, get_task
from atlas.core.exceptions import TaskInactionException
from atlas.conditions import SchedulerCycles, SchedulerStarted, TaskFinished, TaskStarted, AlwaysFalse, AlwaysTrue
from atlas.core.parameters import GLOBAL_PARAMETERS
from atlas import session

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

def test_creating_child(tmpdir):
    with tmpdir.as_cwd() as old_dir:
        session.reset()
        # To be confident the scheduler won't lie to us
        # we test the task execution with a job that has
        # actual measurable impact outside atlas
        scheduler = Scheduler(
            tasks=[
                FuncTask(run_creating_child, name="task_1", start_cond=AlwaysTrue()),
            ], 
            shut_condition=TaskStarted(task="task_1") >= 1,
            tasks_as_daemon=False
        )

        scheduler()

        history = get_task("task_1").get_history()
        assert 1 == (history["action"] == "run").sum()
        assert 1 == (history["action"] == "success").sum()
        assert 0 == (history["action"] == "fail").sum()

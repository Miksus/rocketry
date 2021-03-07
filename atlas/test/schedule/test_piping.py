
from atlas.task import FuncTask
from atlas.core import Task, Scheduler
from atlas.conditions import SchedulerCycles, TaskFinished, TaskStarted, DependSuccess

from atlas import session

import pytest
import logging
import sys
import time
import os


def run_failing():
    raise RuntimeError("Task failed")

def run_succeeding():
    pass

def run_slow():
    time.sleep(30)

def create_line_to_file():
    with open("work.txt", "a") as file:
        file.write("line created\n")

@pytest.mark.parametrize("execution", ["main", "thread", "process"])
def test_dependent(tmpdir, execution):
    with tmpdir.as_cwd() as old_dir:
        session.reset()

        # Running the master tasks only once
        task_a = FuncTask(run_succeeding, name="A", start_cond=~TaskStarted(task="A"), execution=execution)
        task_b = FuncTask(run_succeeding, name="B", start_cond=~TaskStarted(task="B"), execution=execution)

        task_after_a = FuncTask(
            run_succeeding, 
            name="After A", 
            start_cond=DependSuccess(depend_task="A"),
            execution=execution
        )
        task_after_b = FuncTask(
            run_succeeding, 
            name="After B", 
            start_cond=DependSuccess(depend_task="B"),
            execution=execution
        )
        task_after_all = FuncTask(
            run_succeeding, 
            name="After all", 
            start_cond=DependSuccess(depend_task="After A") & DependSuccess(depend_task="After B"),
            execution=execution
        )

        scheduler = Scheduler(
            shut_condition=TaskStarted(task="After all") >= 1
        )

        scheduler()

        history = session.get_task_log()
        history = history.set_index("action")

        a_start = history[(history["task_name"] == "A")].loc["run", "asctime"]
        b_start = history[(history["task_name"] == "B")].loc["run", "asctime"]
        after_a_start = history[(history["task_name"] == "After A")].loc["run", "asctime"]
        after_b_start = history[(history["task_name"] == "After B")].loc["run", "asctime"]
        after_all_start = history[(history["task_name"] == "After all")].loc["run", "asctime"]
        
        assert a_start < after_a_start < after_all_start
        assert b_start < after_b_start < after_all_start
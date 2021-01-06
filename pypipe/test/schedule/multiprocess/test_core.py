
from pypipe.core import MultiScheduler
from pypipe.builtin.task import FuncTask
from pypipe.core.task.base import Task, clear_tasks
from pypipe.builtin.conditions import SchedulerCycles, TaskFinished, TaskStarted
from pypipe.core.parameters import GLOBAL_PARAMETERS
from pypipe.core import reset
from pypipe.builtin.session import session

import pytest
import logging
import sys
import time
import os

# TODO:
#   Test maintainer task 
#   Test parametrization (parameter passing)
#   Test scheduler crashing

# Task funcs
def run_failing():
    raise RuntimeError("Task failed")

def run_succeeding():
    pass

def run_slow():
    time.sleep(30)

def create_line_to_file():
    with open("work.txt", "a") as file:
        file.write("line created\n")

def run_with_param(int_5):
    assert int_5 == 5

def test_task_execution(tmpdir):
    reset()
    with tmpdir.as_cwd() as old_dir:
        # To be confident the scheduler won't lie to us
        # we test the task execution with a job that has
        # actual measurable impact outside pypipe
        scheduler = MultiScheduler(
            [
                FuncTask(create_line_to_file, name="add line to file"),
            ], 
            shut_condition=TaskStarted(task="add line to file") >= 3,
        )

        scheduler()

        with open("work.txt", "r") as file:
            assert 3 == len(list(file))


@pytest.mark.parametrize(
    "task_func,run_count,fail_count,success_count",
    [
        pytest.param(
            run_succeeding, 
            3, 0, 3,
            id="Succeeding task"),

        pytest.param(
            run_failing, 
            3, 3, 0,
            id="Failing task"),
    ],
)
def test_task_log(tmpdir, task_func, run_count, fail_count, success_count):
    reset()
    with tmpdir.as_cwd() as old_dir:
        task = FuncTask(task_func, name="task")

        scheduler = MultiScheduler(
            [
                task,
            ], shut_condition=TaskStarted(task="task") >= run_count
        )
        scheduler()

        history = task.get_history()
        assert run_count == (history["action"] == "run").sum()
        assert success_count == (history["action"] == "success").sum()
        assert fail_count == (history["action"] == "fail").sum()


def test_task_timeout(tmpdir):
    reset()
    with tmpdir.as_cwd() as old_dir:
        task = FuncTask(run_slow, name="slow task")

        scheduler = MultiScheduler(
            [
                task,
            ], 
            shut_condition=TaskStarted(task="slow task") >= 2,
            timeout="1 seconds"
        )
        scheduler()

        history = task.get_history()
        assert 2 == (history["action"] == "run").sum()
        assert 2 == (history["action"] == "terminate").sum()
        assert 0 == (history["action"] == "success").sum()
        assert 0 == (history["action"] == "fail").sum()


def test_priority(tmpdir):
    reset()
    with tmpdir.as_cwd() as old_dir:
        FuncTask.set_default_logger()

        task_1 = FuncTask(run_succeeding, priority=1, name="first")
        task_2 = FuncTask(run_failing, priority=10, name="last")
        task_3 = FuncTask(run_failing, priority=5, name="second")
        scheduler = MultiScheduler(
            [
                task_1,
                task_2,
                task_3
            ], shut_condition=TaskStarted(task="last") >= 1
        )

        scheduler()
        assert scheduler.n_cycles == 1

        history = session.get_task_log()
        history = history.set_index("action")

        task_1_start = history[(history["task_name"] == "first")].loc["run", "asctime"]
        task_3_start = history[(history["task_name"] == "second")].loc["run", "asctime"]
        task_2_start = history[(history["task_name"] == "last")].loc["run", "asctime"]
        
        assert task_1_start < task_3_start < task_2_start

def test_pass_params(tmpdir):
    reset()
    with tmpdir.as_cwd() as old_dir:
        task = FuncTask(run_with_param, name="parametrized")
        scheduler = MultiScheduler(
            [
                task,
            ], shut_condition=TaskStarted(task="parametrized") >= 1
        )
        GLOBAL_PARAMETERS["int_5"] = 5
        GLOBAL_PARAMETERS["extra_param"] = "something"
        scheduler()

        history = task.get_history()
        assert 1 == (history["action"] == "run").sum()
        assert 1 == (history["action"] == "success").sum()
        assert 0 == (history["action"] == "fail").sum()
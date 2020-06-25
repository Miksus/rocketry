
from pypipe import Scheduler, MultiScheduler, FuncTask
from pypipe.task.base import Task, clear_tasks
from pypipe.conditions import scheduler_cycles

from pypipe.conditions import task_ran, task_failed, task_succeeded

from pypipe import reset

import pytest
import logging
import sys


def myfunc():
    print("The task is running")

def failing():
    raise TypeError("Failed task")

def succeeding():
    print("Success")

def test_task_in_startcond(tmpdir):
    reset()
    with tmpdir.as_cwd() as old_dir:


        task_run_once_a = FuncTask(succeeding, ~task_ran, name="once_a")
        task_run_once_b = FuncTask(succeeding, ~task_succeeded, name="once_b")
        task_wont_run_a = FuncTask(succeeding, task_ran, name="never_a")
        task_wont_run_b = FuncTask(failing, task_failed, name="never_b")

        scheduler = MultiScheduler(
            [
                task_run_once_a,
                task_run_once_b,
                task_wont_run_a,
                task_wont_run_b,
            ], shut_condition=scheduler_cycles >= 3
        )
        
        scheduler()

        history = task_run_once_a.get_history()
        print(history)
        assert 1 == (history["action"] == "run").sum()
        assert 1 == (history["action"] == "success").sum()
        assert 0 == (history["action"] == "fail").sum()

        history = task_run_once_b.get_history()
        assert 1 == (history["action"] == "run").sum()
        assert 1 == (history["action"] == "success").sum()
        assert 0 == (history["action"] == "fail").sum()

        history = task_wont_run_a.get_history()
        assert 0 == (history["action"] == "run").sum()
        assert 0 == (history["action"] == "success").sum()
        assert 0 == (history["action"] == "fail").sum()

        history = task_wont_run_b.get_history()
        assert 0 == (history["action"] == "run").sum()
        assert 0 == (history["action"] == "success").sum()
        assert 0 == (history["action"] == "fail").sum()

def test_dependent(tmpdir):
    reset()
    with tmpdir.as_cwd() as old_dir:
        

        task_a = FuncTask(succeeding, name="a")
        task_b = FuncTask(succeeding, name="b")
        task_c = FuncTask(failing, name="c") # Failing task

        dependent_succeeding = FuncTask(succeeding, dependent=["a", "b"], name="dependent_success")
        dependent_not_running = FuncTask(succeeding, dependent=["c", "b"], name="dependent_not_ran")
        scheduler = MultiScheduler(
            [
                task_a,
                task_b,
                task_c,
                dependent_succeeding,
                dependent_not_running,
            ], shut_condition=scheduler_cycles >= 3
        )
        
        scheduler()

        history = dependent_succeeding.get_history()
        assert 3 == (history["action"] == "run").sum()
        assert 3 == (history["action"] == "success").sum()
        assert 0 == (history["action"] == "fail").sum()

        history = dependent_not_running.get_history()
        assert 0 == (history["action"] == "run").sum()
        assert 0 == (history["action"] == "success").sum()
        assert 0 == (history["action"] == "fail").sum()


def test_execution(tmpdir):
    reset()
    with tmpdir.as_cwd() as old_dir:
        FuncTask.set_default_logger()

        task_1 = FuncTask(succeeding, execution="", name="first")
        task_2 = FuncTask(failing, priority=10, name="last")
        task_3 = FuncTask(failing, priority=5, name="second")
        scheduler = Scheduler(
            [
                task_1,
                task_2,
                task_3
            ], shut_condition=scheduler_cycles >= 1
        )
        
        scheduler()

        history = scheduler.get_history()
        history = history.set_index("action")

        task_1_start = history[(history["task_name"] == "first")].loc["run", "asctime"]
        task_3_start = history[(history["task_name"] == "second")].loc["run", "asctime"]
        task_2_start = history[(history["task_name"] == "last")].loc["run", "asctime"]
        
        assert task_1_start < task_3_start < task_2_start


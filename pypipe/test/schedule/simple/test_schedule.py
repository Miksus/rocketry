
from pypipe import Scheduler, MultiScheduler, FuncTask
from pypipe.task.base import Task, clear_tasks
from pypipe.conditions import scheduler_cycles
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

def test_simple(tmpdir):
    reset()
    with tmpdir.as_cwd() as old_dir:


        task_success = FuncTask(succeeding)
        task_fail = FuncTask(failing)
        scheduler = Scheduler(
            [
                task_success,
                task_fail
            ], shut_condition=scheduler_cycles >= 3
        )
        
        scheduler()
        assert scheduler.n_cycles == 3

        print(task_success.logger.logger.handlers[0].baseFilename)
        print("Success name:", task_success.name)
        print("Failure name:", task_fail.name)

        history = task_success.get_history()
        assert 3 == (history["action"] == "run").sum()
        assert 3 == (history["action"] == "success").sum()
        assert 0 == (history["action"] == "fail").sum()

        history = task_fail.get_history()
        assert 3 == (history["action"] == "run").sum()
        assert 0 == (history["action"] == "success").sum()
        assert 3 == (history["action"] == "fail").sum()

def test_simple_multiprocess(tmpdir):
    reset()
    with tmpdir.as_cwd() as old_dir:
        

        task_success = FuncTask(succeeding)
        task_fail = FuncTask(failing)
        scheduler = MultiScheduler(
            [
                task_success,
                task_fail
            ], shut_condition=scheduler_cycles >= 3
        )
        
        scheduler()
        assert scheduler.n_cycles == 3

        print(task_success.logger.logger.handlers[0].baseFilename)
        print("Success name:", task_success.name)
        print("Failure name:", task_fail.name)

        history = task_success.get_history()
        print(history)
        assert 3 == (history["action"] == "run").sum()
        assert 3 == (history["action"] == "success").sum()
        assert 0 == (history["action"] == "fail").sum()

        history = task_fail.get_history()
        print(history)
        assert 3 == (history["action"] == "run").sum()
        assert 0 == (history["action"] == "success").sum()
        assert 3 == (history["action"] == "fail").sum()


def test_priority(tmpdir):
    reset()
    with tmpdir.as_cwd() as old_dir:
        FuncTask.set_default_logger()

        task_1 = FuncTask(succeeding, priority=1, name="first")
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
        assert scheduler.n_cycles == 1

        print(task_1.logger.logger.handlers[0].baseFilename)
        print("Task 1 name:", task_1.name)
        print("Task 2 name:", task_2.name)
        print("Task 3 name:", task_3.name)

        history = scheduler.get_history()
        history = history.set_index("action")

        print(history)
        print("Logger file", Task.get_logger().handlers[0].baseFilename)
        print("Logger cont", Task.get_logger().handlers[0].read())

        task_1_start = history[(history["task_name"] == "first")].loc["run", "asctime"]
        task_3_start = history[(history["task_name"] == "second")].loc["run", "asctime"]
        task_2_start = history[(history["task_name"] == "last")].loc["run", "asctime"]
        
        assert task_1_start < task_3_start < task_2_start


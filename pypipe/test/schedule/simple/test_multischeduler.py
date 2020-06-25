

from pypipe import Scheduler, MultiScheduler, FuncTask
from pypipe.task.base import Task, clear_tasks
from pypipe.conditions import scheduler_cycles
from pypipe import reset

import pytest
import logging
import sys
import time

def run_forever():
    while True:
        time.sleep(60*60)

def slow_func():
    time.sleep(3)

def succeeding():
    print("Success")

def test_termination(tmpdir):
    reset()
    with tmpdir.as_cwd() as old_dir:
        task = FuncTask(run_forever, timeout=5, name="a_task")
        scheduler = MultiScheduler([task])
        scheduler.setup()
        
        scheduler.run_task_as_process(task)
        scheduler.terminate_task(task)
        assert not scheduler.is_alive(task)

        history = task.get_history()
        assert 1 == (history["action"] == "run").sum()
        assert 0 == (history["action"] == "success").sum()
        assert 0 == (history["action"] == "fail").sum()
        assert 1 == (history["action"] == "terminate").sum()


def test_timeout(tmpdir):
    reset()
    with tmpdir.as_cwd() as old_dir:
        

        task_success = FuncTask(slow_func, timeout=5, name="successing")
        task_terminated = FuncTask(slow_func, timeout=1, name="failing")
        scheduler = MultiScheduler(
            [
                task_success,
                task_terminated
            ], shut_condition=scheduler_cycles >= 1, min_sleep=0.5
        )
        
        scheduler()

        history = task_success.get_history()
        assert 1 == (history["action"] == "run").sum()
        assert 1 == (history["action"] == "success").sum()
        assert 0 == (history["action"] == "fail").sum()

        history = task_terminated.get_history()
        print(history)
        assert 1 == (history["action"] == "run").sum()
        assert 0 == (history["action"] == "success").sum()
        assert 0 == (history["action"] == "fail").sum()
        assert 1 == (history["action"] == "terminate").sum()
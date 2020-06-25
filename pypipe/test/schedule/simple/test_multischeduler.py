

from pypipe import Scheduler, MultiScheduler, FuncTask
from pypipe.task.base import Task, clear_tasks
from pypipe.conditions import scheduler_cycles
from pypipe import reset

import pytest
import logging
import sys
import time

def slow_func():
    time.sleep(3)

def succeeding():
    print("Success")

def test_timeout(tmpdir):
    reset()
    with tmpdir.as_cwd() as old_dir:
        

        task_success = FuncTask(slow_func, timeout=5, name="successing")
        task_fail = FuncTask(slow_func, timeout=1, name="failing")
        scheduler = MultiScheduler(
            [
                task_success,
                task_fail
            ], shut_condition=scheduler_cycles >= 1
        )
        
        scheduler()

        history = task_success.get_history()
        assert 1 == (history["action"] == "run").sum()
        assert 1 == (history["action"] == "success").sum()
        assert 0 == (history["action"] == "fail").sum()

        history = task_fail.get_history()
        print(history)
        assert 1 == (history["action"] == "run").sum()
        assert 0 == (history["action"] == "success").sum()
        assert 1 == (history["action"] == "fail").sum()
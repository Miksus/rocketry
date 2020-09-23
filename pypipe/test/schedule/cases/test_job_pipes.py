

from pypipe import Scheduler, MultiScheduler, FuncTask
from pypipe.task.base import Task, clear_tasks
from pypipe.conditions import scheduler_cycles, task_ran, scheduler_started
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
        sched = MultiScheduler([
            FuncTask(do_continuously, start_cond=~task_ran.past("5 seconds"), name="Task A continuous"),
            FuncTask(do_continuously, start_cond=~task_ran.past("5 seconds"), name="Task B continuous"),
            FuncTask(do_minutely, start_cond=~task_ran.in_cycle("minutely"), name="Task C"),
        ])
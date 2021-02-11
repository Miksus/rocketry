from atlas.core import Scheduler
from atlas.task import FuncTask
from atlas.time import TimeDelta
from atlas.core.task.base import Task, clear_tasks, get_task
from atlas.conditions import SchedulerCycles, SchedulerStarted, TaskFinished, TaskStarted, AlwaysFalse, AlwaysTrue
from atlas.core.parameters import GLOBAL_PARAMETERS
from atlas import session

import os

def create_line_to_startup_file():
    with open("start.txt", "w") as file:
        file.write("line created\n")

def create_line_to_shutdown():
    with open("shut.txt", "w") as file:
        file.write("line created\n")

def test_tasks_startup_shutdown(tmpdir):
    with tmpdir.as_cwd() as old_dir:
        session.reset()

        scheduler = Scheduler(
            tasks=[],
            startup_tasks=[
                FuncTask(create_line_to_startup_file, name="startup"),
            ],
            shutdown_tasks=[
                FuncTask(create_line_to_shutdown, name="shutdown"),
            ],
            shut_condition=AlwaysTrue()
        )

        scheduler()
        
        assert not session.get_task_log().empty
        assert not session.get_scheduler_log().empty
from atlas.core import Scheduler
from atlas.task import FuncTask
from atlas.conditions import AlwaysTrue
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

        FuncTask(create_line_to_startup_file, name="startup", on_startup=True)
        FuncTask(create_line_to_shutdown, name="shutdown", on_shutdown=True)
        scheduler = Scheduler(
            shut_condition=AlwaysTrue()
        )

        scheduler()
        
        assert not session.get_task_log().empty
        assert not session.get_scheduler_log().empty
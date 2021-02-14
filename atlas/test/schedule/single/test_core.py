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

def create_line_to_file():
    with open("work.txt", "a") as file:
        file.write("line created\n")

def run_maintainer_with_params(_scheduler_, _task_):
    assert isinstance(_scheduler_, Scheduler)
    _scheduler_.name = "maintained scheduler"
    assert _task_.name == "maintainer"

def run_maintainer():
    pass

def test_task_execution(tmpdir):
    with tmpdir.as_cwd() as old_dir:
        session.reset()
        # To be confident the scheduler won't lie to us
        # we test the task execution with a job that has
        # actual measurable impact outside atlas
        scheduler = Scheduler(
            [
                FuncTask(create_line_to_file, name="add line to file", start_cond=AlwaysTrue(), execution="single"),
            ], 
            shut_condition=TaskStarted(task="add line to file") >= 3,
        )

        scheduler()

        with open("work.txt", "r") as file:
            assert 3 == len(list(file))

def test_task_with_params(tmpdir):
    with tmpdir.as_cwd() as old_dir:
        session.reset()
        # To be confident the scheduler won't lie to us
        # we test the task execution with a job that has
        # actual measurable impact outside atlas
        scheduler = Scheduler(
            tasks=[
                FuncTask(run_maintainer_with_params, name="maintainer", start_cond=AlwaysTrue(), execution="single"),
            ],
            shut_condition=TaskStarted(task="maintainer") >= 1,
            name="unmaintained scheduler"
        )

        scheduler()

        history = get_task("maintainer").get_history()
        assert 1 == (history["action"] == "run").sum()
        assert 1 == (history["action"] == "success").sum()
        assert 0 == (history["action"] == "fail").sum()

        assert scheduler.name == "maintained scheduler"


def test_tasks_startup_shutdown(tmpdir):
    with tmpdir.as_cwd() as old_dir:
        session.reset()

        scheduler = Scheduler(
            tasks=[
                FuncTask(create_line_to_startup_file, name="startup", execution="single", on_startup=True),
                FuncTask(create_line_to_shutdown, name="shutdown", execution="single", on_shutdown=True),
            ],
            shut_condition=AlwaysTrue()
        )

        scheduler()
        
        assert os.path.exists("start.txt")
        assert os.path.exists("shut.txt")
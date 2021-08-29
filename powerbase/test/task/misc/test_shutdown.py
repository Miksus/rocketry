from powerbase.core.conditions.base import AlwaysFalse, AlwaysTrue
from powerbase.task.maintain import ShutDown
from powerbase.task import FuncTask
from powerbase.core.exceptions import SchedulerExit
import pytest

from powerbase.core import Scheduler, parameters
from powerbase.time import TimeDelta
from powerbase.conditions import SchedulerStarted, TaskStarted

import pytest
import logging
def write_file(text):
    with open("test.txt", "a") as f:
        f.write(text)

def test_restart_raises(session):
    task = ShutDown()
    with pytest.raises(SchedulerExit):
        task()

def test_scheduler_shutdown(tmpdir, session):

    with tmpdir.as_cwd() as old_dir:
        
        FuncTask(write_file, parameters={"text": "Started"}, on_startup=True, name="write_startup", execution="main")
        FuncTask(write_file, parameters={"text": "Shut"}, on_shutdown=True, name="write_shutdown", execution="main")

        task = ShutDown()

        task.force_run = True
        
        scheduler = Scheduler(shut_condition=AlwaysFalse())
        scheduler()

        with open("test.txt") as f:
            cont = f.read()
        assert "StartedShut" == cont

        history = list(task.get_history())
        assert 1 == len([record for record in history if record["action"] == "run"])
        assert 1 == len([record for record in history if record["action"] == "success"])

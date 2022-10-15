import pytest

from rocketry.tasks.maintain import Restart
from rocketry.tasks import FuncTask
from rocketry.exc import SchedulerRestart
from rocketry.conditions import TaskStarted



def write_file(text):
    with open("test.txt", "a", encoding="utf-8") as f:
        f.write(text)

def test_restart_raises(session):
    task = Restart(session=session)
    with pytest.raises(SchedulerRestart):
        task()

def test_scheduler_restart(tmpdir, session):

    with tmpdir.as_cwd():

        FuncTask(write_file, parameters={"text": "Started"}, on_startup=True, name="startup", execution="main", session=session)
        FuncTask(write_file, parameters={"text": "Shut"}, on_shutdown=True, name="shutdown", execution="main", session=session)

        task = Restart(session=session)

        task.run()

        session.config.shut_cond = TaskStarted(task=task) == 1
        session.config.restarting = "recall"

        session.start()

        with open("test.txt", encoding="utf-8") as f:
            cont = f.read()
        assert "StartedShutStartedShut" == cont

        records = list(map(lambda e: e.dict(exclude={'created'}), task.logger.get_records()))
        assert 1 == len([record for record in records if record["action"] == "run"])
        assert 1 == len([record for record in records if record["action"] == "success"])

# TODO: Test

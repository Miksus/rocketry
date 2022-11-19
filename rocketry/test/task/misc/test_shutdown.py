import pytest

from rocketry.conditions import AlwaysFalse
from rocketry.tasks.maintain import ShutDown
from rocketry.tasks import FuncTask
from rocketry.exc import SchedulerExit

def write_file(text):
    with open("test.txt", "a", encoding="utf-8") as f:
        f.write(text)

def test_restart_raises(session):
    task = ShutDown(session=session)
    with pytest.raises(SchedulerExit):
        task()

def test_scheduler_shutdown(tmpdir, session):

    with tmpdir.as_cwd():

        FuncTask(write_file, parameters={"text": "Started"}, on_startup=True, name="write_startup", execution="main", session=session)
        FuncTask(write_file, parameters={"text": "Shut"}, on_shutdown=True, name="write_shutdown", execution="main", session=session)

        task = ShutDown(session=session)

        task.run()

        session.config.shut_cond = AlwaysFalse()

        session.start()

        with open("test.txt", encoding="utf-8") as f:
            cont = f.read()
        assert "StartedShut" == cont

        records = list(map(lambda e: e.dict(exclude={'created'}), task.logger.get_records()))
        assert 1 == len([record for record in records if record["action"] == "run"])
        assert 1 == len([record for record in records if record["action"] == "success"])

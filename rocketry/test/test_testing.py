import datetime

import pytest
from rocketry.testing.log import create_task_record

def test_create_record(session):
    ts = int(datetime.datetime(2022, 1, 1).timestamp())
    rec = create_task_record(task_name="mytask", action="run", created="2022-01-01")
    assert rec.task_name == "mytask"
    assert rec.action == "run"
    assert rec.created == ts
    assert rec.levelname == "INFO"
    assert rec.name == session.config.task_logger_basename

    rec = create_task_record(task_name="mytask", action="success", created=datetime.datetime(2022, 1, 1))
    assert rec.task_name == "mytask"
    assert rec.action == "success"
    assert rec.created == ts
    assert rec.levelname == "INFO"

    rec = create_task_record(task_name="mytask", action="fail", created=ts)
    assert rec.task_name == "mytask"
    assert rec.action == "fail"
    assert rec.created == ts
    assert rec.levelname == "ERROR"

    with pytest.raises(ValueError):
        create_task_record(task_name="mytask", action="typo", created=ts)


import logging

import pytest
from rocketry.core.log.adapter import TaskAdapter
from rocketry.tasks import FuncTask
from rocketry.core import Parameters, Scheduler
from rocketry import Session

def test_shutdown(session):
    assert not session.scheduler._flag_shutdown.is_set()
    with pytest.warns(DeprecationWarning):
        session.shutdown()
    assert session.scheduler._flag_shutdown.is_set()

def test_config_silence_task_prerun():
    s = Session()
    assert not s.config.silence_task
    
    with pytest.warns(DeprecationWarning):
        s = Session(config={"silence_task_prerun": True})
    assert s.config.silence_task

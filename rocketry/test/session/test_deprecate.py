
import logging

import pytest
from rocketry.core.log.adapter import TaskAdapter
from rocketry.tasks import FuncTask
from rocketry.core import Parameters, Scheduler

def test_shutdown(session):
    assert not session.scheduler._flag_shutdown.is_set()
    with pytest.warns(DeprecationWarning):
        session.shutdown()
    assert session.scheduler._flag_shutdown.is_set()
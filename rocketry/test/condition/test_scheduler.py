import datetime

import pytest

from rocketry.conditions import (
    SchedulerStarted,
    SchedulerCycles
)
from rocketry.time import (
    TimeDelta,
)

def test_scheduler_cycles(session):

    session.config.shut_cond = SchedulerCycles.from_magic(__eq__=3)
    session.start()
    # Imitating the __bool__
    assert (SchedulerCycles() == 3).observe(session=session)
    assert (SchedulerCycles() > 2).observe(session=session)
    assert (SchedulerCycles() < 4).observe(session=session)
    assert (SchedulerCycles() != 4).observe(session=session)
    assert not (SchedulerCycles() < 3).observe(session=session)
    assert not (SchedulerCycles() > 3).observe(session=session)
    assert not (SchedulerCycles() == 4).observe(session=session)

    with pytest.raises(ValueError):
        SchedulerCycles.from_magic(invalid=3)

def test_scheduler_started(session):

    session.scheduler.startup_time = datetime.datetime.now() - datetime.timedelta(0, 20, 0) # 20 seconds ago
    # Imitating the __bool__
    assert SchedulerStarted().observe(session=session)
    assert (SchedulerStarted(period=TimeDelta("30 seconds"))).observe(session=session)
    assert not (SchedulerStarted(period=TimeDelta("10 seconds"))).observe(session=session)

def test_cycles_string():
    assert str(SchedulerCycles() == 3) == "scheduler has 3 cycles"

    assert str(SchedulerCycles() > 3) == "scheduler has more than 3 cycles"
    assert str(SchedulerCycles() < 3) == "scheduler has less than 3 cycles"

    assert str(SchedulerCycles() >= 3) == "scheduler has more or equal than 3 cycles"
    assert str(SchedulerCycles() <= 3) == "scheduler has less or equal than 3 cycles"

def test_started_string():
    assert str(SchedulerStarted(period=TimeDelta("30 seconds")))

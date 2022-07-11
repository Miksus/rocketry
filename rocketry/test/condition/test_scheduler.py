
import datetime

from rocketry.conditions import (
    SchedulerStarted,
    SchedulerCycles
)
from rocketry.time import (
    TimeDelta, 
    TimeOfDay
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


def test_scheduler_started(session):

    session.scheduler.startup_time = datetime.datetime.now() - datetime.timedelta(0, 20, 0) # 20 seconds ago
    # Imitating the __bool__
    assert (SchedulerStarted(period=TimeDelta("30 seconds"))).observe(session=session)
    assert not (SchedulerStarted(period=TimeDelta("10 seconds"))).observe(session=session)

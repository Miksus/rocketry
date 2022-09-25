from rocketry.time import TimeDelta
from rocketry.conditions import SchedulerCycles, SchedulerStarted

def test_scheduler_started(session):

    session.config.shut_cond = ~SchedulerStarted(period=TimeDelta("1 second"))
    session.start()

    assert session.scheduler.n_cycles > 1

def test_scheduler_cycles(session):

    session.config.shut_cond = SchedulerCycles() >= 4
    session.start()

    assert session.scheduler.n_cycles == 4

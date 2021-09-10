
from redengine.core import Scheduler
from redengine.time import TimeDelta
from redengine.conditions import SchedulerCycles, SchedulerStarted

import pytest


def test_scheduler_started(tmpdir, session):
    with tmpdir.as_cwd() as old_dir:

        scheduler = Scheduler(
            [], shut_cond=~SchedulerStarted(period=TimeDelta("1 second"))
        )
        scheduler()

        assert scheduler.n_cycles > 1

def test_scheduler_cycles(tmpdir, session):
    with tmpdir.as_cwd() as old_dir:

        scheduler = Scheduler(
            [], shut_cond=SchedulerCycles() >= 4
        )
        scheduler()

        assert scheduler.n_cycles == 4
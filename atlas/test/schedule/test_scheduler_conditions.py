
from atlas.core import Scheduler
from atlas.time import TimeDelta
from atlas.conditions import SchedulerCycles, SchedulerStarted

import pytest


def test_scheduler_started(tmpdir, session):
    with tmpdir.as_cwd() as old_dir:

        scheduler = Scheduler(
            [], shut_condition=~SchedulerStarted(period=TimeDelta("1 second"))
        )
        scheduler()

        assert scheduler.n_cycles > 1

def test_scheduler_cycles(tmpdir, session):
    with tmpdir.as_cwd() as old_dir:

        scheduler = Scheduler(
            [], shut_condition=SchedulerCycles() >= 4
        )
        scheduler()

        assert scheduler.n_cycles == 4
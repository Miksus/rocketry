
from atlas.core import MultiScheduler
from atlas.time import TimeDelta
from atlas.conditions import SchedulerCycles, SchedulerStarted
from atlas import session

import pytest


def test_scheduler_started(tmpdir):
    with tmpdir.as_cwd() as old_dir:
        session.reset()

        scheduler = MultiScheduler(
            [], shut_condition=~SchedulerStarted(period=TimeDelta("1 second"))
        )
        scheduler()

        assert scheduler.n_cycles > 1

def test_scheduler_cycles(tmpdir):
    with tmpdir.as_cwd() as old_dir:
        session.reset()

        scheduler = MultiScheduler(
            [], shut_condition=SchedulerCycles() >= 4
        )
        scheduler()

        assert scheduler.n_cycles == 4
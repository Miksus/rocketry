
from pypipe.core import MultiScheduler
from pypipe.time import TimeDelta
from pypipe.conditions import SchedulerCycles, SchedulerStarted
from pypipe import session

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
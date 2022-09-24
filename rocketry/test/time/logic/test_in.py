import datetime

import pytest

from rocketry.core.time.base import (
    All, Any
)
from rocketry.time.interval import TimeOfDay

from_iso = datetime.datetime.fromisoformat

@pytest.mark.parametrize(
    "dt,periods",
    [
        # Regular
        pytest.param(
            from_iso("2020-01-01 13:00:00"),
            [
                # Valid range should be 12:00 - 14:00
                TimeOfDay("08:00", "18:00"), # Dominant
                TimeOfDay("10:00", "14:00"),
                TimeOfDay("12:00", "16:00"),
            ],
            id="Combination (center)"),
    ],
)
def test_all_in(dt, periods):
    time = All(*periods)
    assert dt in time

@pytest.mark.parametrize(
    "dt,periods",
    [
        # Regular
        pytest.param(
            from_iso("2020-01-01 11:00:00"),
            [
                # Valid range should be 12:00 - 14:00
                TimeOfDay("08:00", "18:00"),
                TimeOfDay("10:00", "14:00"),
                TimeOfDay("12:00", "16:00"),
            ],
            id="Combination (partial outside, left)"),
        pytest.param(
            from_iso("2020-01-01 15:00:00"),
            [
                # Valid range should be 12:00 - 14:00
                TimeOfDay("08:00", "18:00"),
                TimeOfDay("10:00", "14:00"),
                TimeOfDay("12:00", "16:00"),
            ],
            id="Combination (partial outside, right)"),
    ],
)
def test_all_not_in(dt, periods):
    time = All(*periods)
    assert dt not in time


@pytest.mark.parametrize(
    "dt,periods",
    [
        pytest.param(
            from_iso("2020-01-01 08:00:00"),
            [
                TimeOfDay("08:00", "10:00"),
                TimeOfDay("10:00", "14:00"),
                TimeOfDay("14:00", "16:00"),
            ],
            id="Combination (left edge)"),
        pytest.param(
            from_iso("2020-01-01 11:00:00"),
            [
                TimeOfDay("08:00", "10:00"),
                TimeOfDay("10:00", "14:00"),
                TimeOfDay("14:00", "16:00"),
            ],
            id="Combination (center)"),
        pytest.param(
            from_iso("2020-01-01 15:59:59"),
            [
                TimeOfDay("08:00", "10:00"),
                TimeOfDay("10:00", "14:00"),
                TimeOfDay("14:00", "16:00"),
            ],
            id="Combination (right edge)"),
    ],
)
def test_any_in(dt, periods):
    time = Any(*periods)
    assert dt in time

@pytest.mark.parametrize(
    "dt,periods",
    [
        # Regular
        pytest.param(
            from_iso("2020-01-01 07:00:00"),
            [
                TimeOfDay("08:00", "10:00"),
                TimeOfDay("10:00", "14:00"),
                TimeOfDay("14:00", "16:00"),
            ],
            id="Combination (left)"),
        pytest.param(
            from_iso("2020-01-01 17:00:00"),
            [
                TimeOfDay("08:00", "10:00"),
                TimeOfDay("10:00", "14:00"),
                TimeOfDay("14:00", "16:00"),
            ],
            id="Combination (right)"),
    ],
)
def test_any_not_in(dt, periods):
    time = Any(*periods)
    assert dt not in time

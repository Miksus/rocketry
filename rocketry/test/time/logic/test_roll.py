import datetime

import pytest

from rocketry.core.time.base import (
    All, Any
)
from rocketry.time.interval import TimeOfDay, TimeOfMinute

from_iso = datetime.datetime.fromisoformat

@pytest.mark.parametrize(
    "dt,periods,roll_start,roll_end",
    [
        # Regular
        pytest.param(
            from_iso("2020-01-01 07:00:00"),
            [
                TimeOfDay("08:00", "18:00"),
                TimeOfDay("10:00", "14:00"),
                TimeOfDay("12:00", "16:00"),
            ],
            from_iso("2020-01-01 12:00:00"), from_iso("2020-01-01 14:00:00"),
            id="Combination"),

        pytest.param(
            from_iso("2020-01-01 07:00:00"),
            [
                TimeOfDay("08:00", "18:00"),
                TimeOfDay("10:00", "14:00"),
                TimeOfDay("11:00", "12:00"),
            ],
            from_iso("2020-01-01 11:00:00"), from_iso("2020-01-01 12:00:00"),
            id="Defined by one"),

        pytest.param(
            from_iso("2020-01-01 12:00:00"),
            [
                TimeOfDay("08:00", "18:00"),
                TimeOfDay("10:00", "14:00"),
                TimeOfDay("12:00", "16:00"),
            ],
            from_iso("2020-01-01 12:00:00"), from_iso("2020-01-01 14:00:00"),
            id="Inside period"),

        pytest.param(
            from_iso("2020-01-01 12:00:00"),
            [
                TimeOfDay("08:00", "18:00"),
                TimeOfMinute(),
            ],
            from_iso("2020-01-01 12:00:00"), from_iso("2020-01-01 12:01:00"),
            id="Cron-like"),
    ],
)
def test_rollforward_all(dt, periods, roll_start, roll_end):
    time = All(*periods)

    interval = time.rollforward(dt)
    assert roll_start == interval.left
    assert roll_end == interval.right

@pytest.mark.parametrize(
    "dt,periods,roll_start,roll_end",
    [
        # Regular
        pytest.param(
            from_iso("2020-01-02 07:00:00"),
            [
                TimeOfDay("08:00", "18:00"),
                TimeOfDay("10:00", "14:00"),
                TimeOfDay("12:00", "16:00"),
            ],
            from_iso("2020-01-01 12:00:00"), from_iso("2020-01-01 14:00:00"),
            id="Combination"),

        pytest.param(
            from_iso("2020-01-01 13:30:00"),
            [
                TimeOfDay("08:00", "18:00"),
                TimeOfDay("10:00", "14:00"),
                TimeOfDay("12:00", "16:00"),
            ],
            from_iso("2020-01-01 12:00:00"), from_iso("2020-01-01 13:30:00"),
            id="Inside period"),
    ],
)
def test_rollback_all(dt, periods, roll_start, roll_end):
    time = All(*periods)

    interval = time.rollback(dt)
    assert roll_start == interval.left
    assert roll_end == interval.right

@pytest.mark.parametrize(
    "dt,periods,roll_start,roll_end",
    [
        # Regular
        pytest.param(
            from_iso("2020-01-01 07:00:00"),
            [
                TimeOfDay("08:00", "18:00"),
                TimeOfDay("10:00", "14:00"),
                TimeOfDay("12:00", "16:00"),
            ],
            from_iso("2020-01-01 08:00:00"), from_iso("2020-01-01 18:00:00"),
            id="Dominant (one interval from start to end)"),

        pytest.param(
            from_iso("2020-01-01 10:00:00"),
            [
                TimeOfDay("08:00", "09:00"),
                TimeOfDay("11:00", "12:00"),
                TimeOfDay("15:00", "18:00"),
            ],
            from_iso("2020-01-01 11:00:00"), from_iso("2020-01-01 12:00:00"),
            id="Sequential (not overlap)"),

        pytest.param(
            from_iso("2020-01-01 07:00:00"),
            [
                TimeOfDay("08:00", "09:00", right_closed=True),
                TimeOfDay("09:00", "12:00", right_closed=True),
                TimeOfDay("12:00", "18:00"),
            ],
            from_iso("2020-01-01 08:00:00"), from_iso("2020-01-01 18:00:00"),
            id="Sequential (overlap)"),

        pytest.param(
            from_iso("2020-01-01 08:30:00"),
            [
                TimeOfDay("08:00", "09:00", right_closed=True),
                TimeOfDay("09:00", "10:00"),
            ],
            from_iso("2020-01-01 08:30:00"), from_iso("2020-01-01 10:00:00"),
            id="On interval"),

        pytest.param(
            from_iso("2020-01-01 07:00:00"),
            [
                TimeOfDay("08:00", "09:00"),
            ],
            from_iso("2020-01-01 08:00:00"), from_iso("2020-01-01 09:00:00"),
            id="Single interval"),
    ],
)
def test_rollforward_any(dt, periods, roll_start, roll_end):
    time = Any(*periods)

    interval = time.rollforward(dt)
    assert roll_start == interval.left
    assert roll_end == interval.right
    assert interval.closed == "left"

@pytest.mark.parametrize(
    "dt,periods,roll_start,roll_end",
    [
        # Regular
        pytest.param(
            from_iso("2020-01-02 07:00:00"),
            [
                TimeOfDay("08:00", "18:00"),
                TimeOfDay("10:00", "14:00"),
                TimeOfDay("12:00", "16:00"),
            ],
            from_iso("2020-01-01 08:00:00"), from_iso("2020-01-01 18:00:00"),
            id="Dominant (one interval from start to end)"),

        pytest.param(
            from_iso("2020-01-01 13:00:00"),
            [
                TimeOfDay("08:00", "09:00"),
                TimeOfDay("11:00", "12:00"),
                TimeOfDay("15:00", "18:00"),
            ],
            from_iso("2020-01-01 11:00:00"), from_iso("2020-01-01 12:00:00"),
            id="Sequential (not overlap)"),

        pytest.param(
            from_iso("2020-01-01 19:00:00"),
            [
                TimeOfDay("08:00", "09:00", right_closed=True),
                TimeOfDay("09:00", "12:00", right_closed=True),
                TimeOfDay("12:00", "18:00"),
            ],
            from_iso("2020-01-01 08:00:00"), from_iso("2020-01-01 18:00:00"),
            id="Sequential (overlap)"),

        pytest.param(
            from_iso("2020-01-01 09:30:00"),
            [
                TimeOfDay("08:00", "09:00", right_closed=True),
                TimeOfDay("09:00", "10:00"),
            ],
            from_iso("2020-01-01 08:00:00"), from_iso("2020-01-01 09:30:00"),
            id="On interval"),

        pytest.param(
            from_iso("2020-01-01 10:00:00"),
            [
                TimeOfDay("08:00", "09:00"),
            ],
            from_iso("2020-01-01 08:00:00"), from_iso("2020-01-01 09:00:00"),
            id="Single interval"),
    ],
)
def test_rollback_any(dt, periods, roll_start, roll_end):
    time = Any(*periods)

    interval = time.rollback(dt)
    assert roll_start == interval.left
    assert roll_end == interval.right

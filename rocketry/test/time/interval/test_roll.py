from datetime import datetime

import pytest

from rocketry.time.interval import (
    TimeOfDay
)

from_iso = datetime.fromisoformat

# TimeOfDay
# ---------

@pytest.mark.parametrize(
    "dt,start,end,roll_start,roll_end",
    [
        # Regular
        pytest.param(
            from_iso("2020-01-01 10:00:00"),
            "10:00", "12:00",
            from_iso("2020-01-01 10:00:00"), from_iso("2020-01-01 12:00:00"),
            id="Left of interval"),
        pytest.param(
            from_iso("2020-01-01 12:00:00"),
            "10:00", "12:00",
            from_iso("2020-01-02 10:00:00"), from_iso("2020-01-02 12:00:00"),
            id="Right of interval"),
        pytest.param(
            from_iso("2020-01-01 11:00:00"),
            "10:00", "12:00",
            from_iso("2020-01-01 11:00:00"), from_iso("2020-01-01 12:00:00"),
            id="Middle of interval"),

        # Overnight
        pytest.param(
            from_iso("2020-01-01 22:00:00"),
            "22:00", "02:00",
            from_iso("2020-01-01 22:00:00"), from_iso("2020-01-02 02:00:00"),
            id="Left of overnight interval"),
        pytest.param(
            from_iso("2020-01-01 02:00:00"),
            "22:00", "02:00",
            from_iso("2020-01-01 22:00:00"), from_iso("2020-01-02 02:00:00"),
            id="Right of overnight interval"),
        pytest.param(
            from_iso("2020-01-01 23:59:59.999999"),
            "22:00", "02:00",
            from_iso("2020-01-01 23:59:59.999999"), from_iso("2020-01-02 02:00:00"),
            id="Middle left of overnight interval"),
        pytest.param(
            from_iso("2020-01-01 00:00:00"),
            "22:00", "02:00",
            from_iso("2020-01-01 00:00:00"), from_iso("2020-01-01 02:00:00"),
            id="Middle right of overnight interval"),

        # Full Cycle
        pytest.param(
            from_iso("2020-01-01 10:00:00"),
            "10:00", "10:00",
            from_iso("2020-01-01 10:00:00"), from_iso("2020-01-02 10:00:00"),
            id="Joint of full interval", marks=pytest.mark.xfail),
        pytest.param(
            from_iso("2020-01-01 12:00:00"),
            "10:00", "10:00",
            from_iso("2020-01-01 12:00:00"), from_iso("2020-01-02 10:00:00"),
            id="Right of full interval"),
        pytest.param(
            from_iso("2020-01-01 09:00:00"),
            "10:00", "10:00",
            from_iso("2020-01-01 09:00:00"), from_iso("2020-01-01 10:00:00"),
            id="Left of full interval"),
    ],
)
def test_rollforward_time_of_day(start, end, dt, roll_start, roll_end):
    time = TimeOfDay(start, end)

    interval = time.rollforward(dt)
    assert roll_start == interval.left
    assert roll_end == interval.right


@pytest.mark.parametrize(
    "dt,start,end,roll_start,roll_end",
    [
        # Regular
        pytest.param(
            from_iso("2020-01-01 10:00:00"),
            "10:00", "12:00",
            from_iso("2020-01-01 10:00:00"), from_iso("2020-01-01 10:00:00"),
            id="Left of interval"),
        pytest.param(
            from_iso("2020-01-01 12:00:00"),
            "10:00", "12:00",
            from_iso("2020-01-01 10:00:00"), from_iso("2020-01-01 12:00:00"),
            id="Right of interval"),
        pytest.param(
            from_iso("2020-01-01 11:00:00"),
            "10:00", "12:00",
            from_iso("2020-01-01 10:00:00"), from_iso("2020-01-01 11:00:00"),
            id="Middle of interval"),

        # Overnight
        pytest.param(
            from_iso("2020-01-01 22:00:00"),
            "22:00", "02:00",
            from_iso("2020-01-01 22:00:00"), from_iso("2020-01-01 22:00:00"),
            id="Left of overnight interval"),
        pytest.param(
            from_iso("2020-01-01 02:00:00"),
            "22:00", "02:00",
            from_iso("2019-12-31 22:00:00"), from_iso("2020-01-01 02:00:00"),
            id="Right of overnight interval"),
        pytest.param(
            from_iso("2020-01-01 23:59:59.999999"),
            "22:00", "02:00",
            from_iso("2020-01-01 22:00:00"), from_iso("2020-01-01 23:59:59.999999"),
            id="Middle left of overnight interval"),
        pytest.param(
            from_iso("2020-01-01 00:00:00"),
            "22:00", "02:00",
            from_iso("2019-12-31 22:00:00"), from_iso("2020-01-01 00:00:00"),
            id="Middle right of overnight interval"),

        # Full Cycle
        pytest.param(
            from_iso("2020-01-01 10:00:00"),
            "10:00", "10:00",
            from_iso("2019-12-31 10:00:00"), from_iso("2020-01-01 10:00:00"),
            id="Joint of full interval", marks=pytest.mark.xfail),
        pytest.param(
            from_iso("2020-01-01 12:00:00"),
            "10:00", "10:00",
            from_iso("2020-01-01 10:00:00"), from_iso("2020-01-01 12:00:00"),
            id="Right of full interval"),
        pytest.param(
            from_iso("2020-01-01 09:00:00"),
            "10:00", "10:00",
            from_iso("2019-12-31 10:00:00"), from_iso("2020-01-01 09:00:00"),
            id="Left of full interval"),
    ],
)
def test_rollback_time_of_day(start, end, dt, roll_start, roll_end):
    time = TimeOfDay(start, end)

    interval = time.rollback(dt)
    assert interval.closed == 'left' if roll_start != roll_end else interval.closed == "both"
    assert roll_start == interval.left
    assert roll_end == interval.right

from datetime import datetime

import pytest

from rocketry.time.interval import (
    TimeOfSecond,
    TimeOfMinute,
    TimeOfHour,
    TimeOfDay,
    TimeOfWeek,
    TimeOfMonth,
)

# TimeOfSecond
# ---------

@pytest.mark.parametrize(
    "dt,time",
    [
        # Regular
        pytest.param(
            datetime(2020, 1, 1, 11, 0, 0, 200_000),
            TimeOfSecond(200, 700),
            id="Left of interval"),
        pytest.param(
            datetime(2020, 1, 1, 11, 0, 0, 700_999),
            TimeOfSecond(200, 700),
            id="Right of interval"),
    ],
)
def test_in_time_of_second(time, dt):
    assert dt in time


@pytest.mark.parametrize(
    "dt,time",
    [
        # Regular
        pytest.param(
            datetime(2020, 1, 1, 11, 0, 0, 199_999),
            TimeOfSecond(200, 700),
            id="Left of interval"),
        pytest.param(
            datetime(2020, 1, 1, 11, 0, 0, 800_000),
            TimeOfSecond(200, 700),
            id="Right of interval"),
    ],
)
def test_not_in_time_of_second(time, dt):
    assert dt not in time

# TimeOfMinute
# ------------

@pytest.mark.parametrize(
    "dt,time",
    [
        # Regular
        pytest.param(
            datetime(2020, 1, 1, 11, 0, 15),
            TimeOfMinute("15.00", "45.00"),
            id="Left of interval"),
        pytest.param(
            datetime(2020, 1, 1, 11, 0, 44, 999_999),
            TimeOfMinute("15.00", "45.00"),
            id="Right of interval"),
    ],
)
def test_in_time_of_minute(time, dt):
    assert dt in time


@pytest.mark.parametrize(
    "dt,time",
    [
        # Regular
        pytest.param(
            datetime(2020, 1, 1, 11, 0, 14, 999_999),
            TimeOfMinute("15.00", "45.00"),
            id="Left of interval"),
        pytest.param(
            datetime(2020, 1, 1, 11, 00, 45, 0),
            TimeOfMinute("15.00", "45.00"),
            id="Right of interval"),
    ],
)
def test_not_in_time_of_minute(time, dt):
    assert dt not in time

# TimeOfHour
# ----------

@pytest.mark.parametrize(
    "dt,time",
    [
        # Regular
        pytest.param(
            datetime(2020, 1, 1, 11, 15),
            TimeOfHour("15:00", "45:00"),
            id="Left of interval"),
        pytest.param(
            datetime(2020, 1, 1, 11, 44, 59, 999_999),
            TimeOfHour("15:00", "45:00"),
            id="Right of interval"),
    ],
)
def test_in_time_of_hour(time, dt):
    assert dt in time

@pytest.mark.parametrize(
    "dt,time",
    [
        # Regular
        pytest.param(
            datetime(2020, 1, 1, 11, 14, 59, 999_999),
            TimeOfHour("15:00", "45:00"),
            id="Left of interval"),
        pytest.param(
            datetime(2020, 1, 1, 11, 45),
            TimeOfHour("15:00", "45:00"),
            id="Right of interval"),
    ],
)
def test_not_in_time_of_hour(time, dt):
    assert dt not in time

# TimeOfDay
# ---------

@pytest.mark.parametrize(
    "dt,start,end",
    [
        # Regular
        pytest.param(
            datetime(2020, 1, 1, 11, 00),
            "10:00", "12:00",
            id="Middle of interval"),

        # Left is closed
        pytest.param(
            datetime(2020, 1, 1, 10, 00),
            "10:00", "12:00",
            id="Left of interval"),
        pytest.param(
            datetime(2020, 1, 1, 22, 00),
            "22:00", "02:00",
            id="Left of overnight interval"),

        # Overnight
        pytest.param(
            datetime(2020, 1, 1, 23, 59, 59, 999999),
            "22:00", "02:00",
            id="Middle left of overnight interval"),
        pytest.param(
            datetime(2020, 1, 1, 00, 00),
            "22:00", "02:00",
            id="Middle right of overnight interval"),

        # Full Cycle
        pytest.param(
            datetime(2020, 1, 1, 10, 00),
            None, None,
            id="Full interval"),
        pytest.param(
            datetime(2020, 1, 1, 10, 00),
            "10:00", "10:00",
            id="Joint of full interval"),
        pytest.param(
            datetime(2020, 1, 1, 12, 00),
            "10:00", "10:00",
            id="Right of full interval"),
        pytest.param(
            datetime(2020, 1, 1, 8, 00),
            "10:00", "10:00",
            id="Left of full interval"),
    ],
)
def test_in_time_of_day(start, end, dt):
    time = TimeOfDay(start, end)
    assert dt in time


@pytest.mark.parametrize(
    "dt,start,end",
    [
        # Regular
        pytest.param(
            datetime(2020, 1, 1, 9, 59, 59, 999999),
            "10:00", "12:00",
            id="Left from interval"),
        pytest.param(
            datetime(2020, 1, 1, 12, 00, 00, 1),
            "10:00", "12:00",
            id="Right from interval"),

        # Right is opened
        pytest.param(
            datetime(2020, 1, 1, 12, 00),
            "10:00", "12:00",
            id="Right of interval"),
        pytest.param(
            datetime(2020, 1, 1, 2, 00),
            "22:00", "02:00",
            id="Right of overnight interval"),

        # Overnight
        pytest.param(
            datetime(2020, 1, 1, 21, 59, 59, 999999),
            "22:00", "02:00",
            id="Left from overnight interval"),
        pytest.param(
            datetime(2020, 1, 1, 2, 00, 00, 1),
            "22:00", "02:00",
            id="Right from overnight interval"),
    ],
)
def test_not_in_time_of_day(start, end, dt):
    time = TimeOfDay(start, end)
    assert dt not in time


# TimeOfWeek
# ----------

# TimeOfWeek
# Year 2024 was chosen as it starts on monday
@pytest.mark.parametrize(
    "dt,start,end",
    [
        # Regular
        pytest.param(
            datetime(2024, 1, 2, 10, 00),
            "Tue 10:00", "Sat 12:00",
            id="Left of interval (with time)"),
        pytest.param(
            datetime(2024, 1, 4, 11, 00),
            "Tue 10:00", "Sat 12:00",
            id="Middle of interval (with time)"),
        pytest.param(
            datetime(2024, 1, 6, 11, 59, 59, 999999),
            "Tue 10:00", "Sat 12:00",
            id="Right of interval (with time)"),
        pytest.param(
            datetime(2024, 1, 6, 23, 59, 59, 999999),
            "Tue", "Sat",
            id="Right of interval"),

        # Over weekend
        pytest.param(
            datetime(2024, 1, 6, 10, 00),
            "Sat 10:00", "Tue 12:00",
            id="Left of over weekend interval (with time)"),
        pytest.param(
            datetime(2024, 1, 7, 23, 59, 59, 999999),
            "Sat 10:00", "Tue 12:00",
            id="Middle left of over weekend interval (with time)"),
        pytest.param(
            datetime(2024, 1, 8, 00, 00),
            "Sat 10:00", "Tue 12:00",
            id="Middle right of over weekend interval (with time)"),

        # Full Cycle
        pytest.param(
            datetime(2024, 1, 1, 00, 00),
            None, None,
            id="Full interval"),
        pytest.param(
            datetime(2024, 1, 2, 00, 00),
            "Tue", "Tue",
            id="Joint of full interval"),
        pytest.param(
            datetime(2024, 1, 1, 00, 00),
            "Tue 00:00", "Tue 00:00",
            id="Right of full interval"),
        pytest.param(
            datetime(2024, 1, 6, 00, 00),
            "Tue 00:00", "Tue 00:00",
            id="Left of full interval"),
    ],
)
def test_in_time_of_week(start, end, dt):
    time = TimeOfWeek(start, end)
    assert dt in time


@pytest.mark.parametrize(
    "dt,start,end",
    [
        # Regular
        pytest.param(
            datetime(2024, 1, 1, 0, 0),
            "Tue 10:00", "Sat 12:00",
            id="Left from interval"),
        pytest.param(
            datetime(2024, 1, 7, 14, 00, 00, 1),
            "Tue 10:00", "Sat 12:00",
            id="Right from interval"),

        # Right is opened
        pytest.param(
            datetime(2024, 1, 6, 12, 00),
            "Tue 10:00", "Sat 12:00",
            id="Right of interval"),
        pytest.param(
            datetime(2024, 1, 9, 12, 00),
            "Sat 10:00", "Tue 12:00",
            id="Right of over weekend interval"),

        # Over weekend
        pytest.param(
            datetime(2024, 1, 6, 9, 59, 59, 999999),
            "Sat 10:00", "Tue 12:00",
            id="Left from over weekend interval"),
        pytest.param(
            datetime(2024, 1, 9, 12, 1, 00),
            "Sat 10:00", "Tue 12:00",
            id="Right from over weekend interval"),
    ],
)
def test_not_in_time_of_week(start, end, dt):
    time = TimeOfWeek(start, end)
    assert dt not in time


# TimeOfMonth
# ---------

@pytest.mark.parametrize(
    "dt,time",
    [
        # Regular
        pytest.param(
            datetime(2020, 1, 2, 11, 00),
            TimeOfMonth("2.", "3."),
            id="Middle of interval"),

        # Left is closed
        pytest.param(
            datetime(2020, 1, 2, 0, 00),
            TimeOfMonth("2.", "3."),
            id="Left of interval"),
        pytest.param(
            datetime(2020, 1, 3, 23, 59, 59, 999999),
            TimeOfMonth("2.", "3."),
            id="Left of overnight interval"),

        # Over month
        pytest.param(
            datetime(2020, 1, 23),
            TimeOfMonth("22.", "2."),
            id="Middle left of over month"),
        pytest.param(
            datetime(2020, 1, 1, 00, 00),
            TimeOfMonth("22.", "2."),
            id="Middle right of over month"),

        # Full Cycle
        pytest.param(
            datetime(2020, 1, 31),
            TimeOfMonth(None, None),
            id="Full interval"),
        pytest.param(
            datetime(2020, 1, 5),
            TimeOfMonth.starting("5."),
            id="Joint of full interval"),
        pytest.param(
            datetime(2020, 1, 1),
            TimeOfMonth.starting("5."),
            id="Right of full interval"),
        pytest.param(
            datetime(2020, 1, 6),
            TimeOfMonth.starting("5."),
            id="Left of full interval"),
    ],
)
def test_in_time_of_month(time, dt):
    assert dt in time


@pytest.mark.parametrize(
    "dt,time",
    [
        # Regular
        pytest.param(
            datetime(2020, 1, 1, 23, 59, 59, 999999),
            TimeOfMonth("2.", "3."),
            id="Left from interval"),
        pytest.param(
            datetime(2020, 1, 4),
            TimeOfMonth("2.", "3."),
            id="Right from interval"),

        # Right is opened
        pytest.param(
            datetime(2020, 1, 21),
            TimeOfMonth("22.", "2."),
            id="Right of over month"),
        pytest.param(
            datetime(2020, 1, 3),
            TimeOfMonth("22.", "2."),
            id="Left of over month"),
    ],
)
def test_not_in_time_of_month(time, dt):
    assert dt not in time

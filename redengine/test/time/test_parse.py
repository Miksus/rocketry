
from redengine.parse import parse_time
from redengine.time import TimeOfDay, TimeOfHour, TimeOfMinute, TimeDelta, TimeOfWeek, TimeOfYear, TimeOfMonth

import pytest

@pytest.mark.parametrize(
    "time_str,expected", [
        pytest.param("every 10 seconds", TimeDelta("10 seconds"), id="every"),

        pytest.param("time of minute between 15:00 and 30:00", TimeOfMinute("15:00", "30:00"), id="TimeOfMinute between"),
        pytest.param("time of minute before 30:00", TimeOfMinute(None, "30:00"), id="TimeOfMinute before"),
        pytest.param("time of minute after 30:00", TimeOfMinute("30:00", None), id="TimeOfMinute after"),

        pytest.param("time of hour between 15:00 and 30:00", TimeOfHour("15:00", "30:00"), id="TimeOfHour between"),
        pytest.param("time of hour before 30:00", TimeOfHour(None, "30:00"), id="TimeOfHour before"),
        pytest.param("time of hour after 30:00", TimeOfHour("30:00", None), id="TimeOfHour after"),

        pytest.param("time of day between 10:00 and 12:00", TimeOfDay("10:00", "12:00"), id="TimeOfDay between"),
        pytest.param("time of day before 12:00", TimeOfDay(None, "12:00"), id="TimeOfDay before"),
        pytest.param("time of day after 12:00", TimeOfDay("12:00", None), id="TimeOfDay after"),

        pytest.param("time of week on Monday", TimeOfWeek("Mon", "Mon"), id="TimeOfWeek on"),
    ]
)
def test_string(time_str, expected):
    cond = parse_time(time_str)
    assert cond == expected
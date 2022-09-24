import datetime

import pytest

from rocketry.core.time.base import StaticInterval
from rocketry.parse import parse_time, ParserError
from rocketry.time import TimeOfDay, TimeOfHour, TimeOfMinute, TimeDelta, TimeOfWeek, TimeOfMonth, always, never

@pytest.mark.parametrize(
    "time_str,expected", [
        pytest.param("always", always, id="always"),
        pytest.param("never", never, id="never"),

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

        pytest.param("time of week on Monday", TimeOfWeek.at("Mon"), id="TimeOfWeek on"),

        pytest.param("time of month between 1st and 2nd", TimeOfMonth("1st", "2nd"), id="TimeOfMonth between (1st, 2nd)"),
        pytest.param("time of month between 3rd and 4th", TimeOfMonth("3rd", "4th"), id="TimeOfMonth between (3rd, 4th)"),

        pytest.param("time of week on Monday | time of week on Friday", TimeOfWeek.at("Mon") | TimeOfWeek.at("Fri"), id="OR"),
        pytest.param("time of week on Monday & time of day between 10:00 and 12:00", TimeOfDay("10:00", "12:00") & TimeOfWeek.at("Mon"), id="AND"),
    ]
)
def test_string(time_str, expected):
    cond = parse_time(time_str)
    assert cond == expected

@pytest.mark.parametrize(
    "t,s,r", [
        pytest.param(always, "always", "always", id="always"),
        pytest.param(never, "never", "never", id="never"),
        pytest.param(
            StaticInterval(datetime.datetime(2022, 1, 1), datetime.datetime(2022, 12, 31)),
            "between 2022-01-01 00:00:00 and 2022-12-31 00:00:00",
            "StaticInterval(start=datetime.datetime(2022, 1, 1, 0, 0), end=datetime.datetime(2022, 12, 31, 0, 0))",
            id="static interval"
        ),
    ]
)
def test_representation(t, s, r):
    assert str(t) == s
    assert repr(t) == r

def test_error():
    with pytest.raises(ParserError):
        cond = parse_time("invalid string")

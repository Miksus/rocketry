from datetime import timedelta, datetime
import pytest
from rocketry.pybox.time import to_timedelta, to_datetime, timedelta_to_str

@pytest.mark.parametrize("s,expected",
    [
        ('00:00:00', timedelta()),
        ('06:05:01', timedelta(hours=6, minutes=5, seconds=1)),
        ('06:05:01.00003', timedelta(hours=6, minutes=5, seconds=1, microseconds=30)),
        ('06:05:01.5', timedelta(hours=6, minutes=5, seconds=1, milliseconds=500)),

        ('1 days 16:05:01.00003', timedelta(days=1, hours=16, minutes=5, seconds=1, microseconds=30)),

        ('10m 20s', timedelta(minutes=10, seconds=20)),
        ('1d 5h 10m 20s', timedelta(days=1, hours=5, minutes=10, seconds=20)),
        ('1d, 5h, 10m, 20s', timedelta(days=1, hours=5, minutes=10, seconds=20)),
        ('5 hr 10 min 20 sec', timedelta(hours=5, minutes=10, seconds=20)),
        ('5 hrs 10 mins 20 secs', timedelta(hours=5, minutes=10, seconds=20)),
        ('1d 5h 10m 20s', timedelta(days=1, hours=5, minutes=10, seconds=20)),
        ("1days 5hours 10minutes 20seconds", timedelta(days=1, hours=5, minutes=10, seconds=20)),
        ("1 day 5 hour 10 minute 20 second", timedelta(days=1, hours=5, minutes=10, seconds=20)),
        ("1 days 5 hours 10 minutes 20 seconds", timedelta(days=1, hours=5, minutes=10, seconds=20)),
        ("-1 days 5 hours 10 minutes 20 seconds", -timedelta(days=1, hours=5, minutes=10, seconds=20)),
        ("--1 days 5 hours 10 minutes 20 seconds", timedelta(days=1, hours=5, minutes=10, seconds=20)),
        ("+1 days 5 hours 10 minutes 20 seconds", timedelta(days=1, hours=5, minutes=10, seconds=20)),
    ]
)
def test_timedelta_from_string(s, expected):
    assert to_timedelta(s) == expected

@pytest.mark.parametrize("unit,n,expected",
    [
        pytest.param('ns', 0, timedelta(), id="0 ns"),
        pytest.param('ns', 1e+9, timedelta(seconds=1), id="nanoseconds"),
        pytest.param('μs', 1e+6, timedelta(seconds=1), id="microseconds"),
        pytest.param('ms', 1000, timedelta(seconds=1), id="milliseconds"),
        pytest.param('s', 1, timedelta(seconds=1), id="seconds"),
        pytest.param('m', 1, timedelta(minutes=1), id="minutes"),
        pytest.param('h', 1, timedelta(hours=1), id="hours"),
    ]
)
def test_timedelta_from_int(unit, n, expected):
    assert to_timedelta(n, unit=unit) == expected

def test_timedelta_from_timedelta():
    assert to_timedelta(timedelta(hours=5)) == timedelta(hours=5)

@pytest.mark.parametrize("obj",
    [
        pytest.param(datetime(2022, 1, 1,), id="datetime"),
        pytest.param(datetime, id="class"),
    ]
)
def test_timedelta_fail(obj):
    with pytest.raises(TypeError):
        to_timedelta(obj)

@pytest.mark.parametrize("dt,kwargs,expected",
    [
        pytest.param(
            timedelta(
                days=400, hours=12, minutes=30, seconds=59, milliseconds=500, microseconds=500
            ), {}, "400 days, 12 hours, 30 minutes, 59 seconds, 500 milliseconds, 500 microseconds",
            id="default"
        ),
        pytest.param(
            timedelta(
                days=435, hours=12, minutes=30, seconds=59, milliseconds=500, microseconds=500
            ), {"include": "all"}, "1 years, 2 months, 1 weeks, 3 days, 12 hours, 30 minutes, 59 seconds, 500 milliseconds, 500 microseconds",
            id="default (all)"
        ),
        pytest.param(
            timedelta(
                days=2,
            ), {}, "2 days",
            id="default (only days)"
        ),
        pytest.param(
            timedelta(
                days=2, seconds=30,
            ), {}, "2 days, 0 hours, 0 minutes, 30 seconds",
            id="default (only days and seconds)"
        ),
        pytest.param(
            timedelta(
                days=2, hours=12, minutes=30, seconds=59, milliseconds=500, microseconds=500
            ), {"format": "short"}, "2d, 12h, 30m, 59s, 500ms, 500μs",
            id="short"
        ),
        pytest.param(
            timedelta(
                days=2, hours=12, minutes=30, seconds=59, milliseconds=500, microseconds=500
            ), {"format": "semishort"}, "2 days, 12 hrs, 30 mins, 59 secs, 500 ms, 500 μs",
            id="semishort"
        ),
        pytest.param(
            timedelta(
                days=16, hours=6
            ),
            {"include": ("weeks", "days", "hours")},
            "2 weeks, 2 days, 6 hours",
            id="include week"
        ),
        pytest.param(
            timedelta(
                days=62, hours=6
            ),
            {"include": ("months", "days", "hours"), "days_in_month": 30},
            "2 months, 2 days, 6 hours",
            id="include month"
        ),
        pytest.param(
            timedelta(
                days=365*2 + 2, hours=6
            ),
            {"include": ("years", "days", "hours"), "days_in_year": 365},
            "2 years, 2 days, 6 hours",
            id="include year"
        ),
    ]
)
def test_timedelta_to_str(dt, kwargs, expected):
    assert timedelta_to_str(dt, **kwargs) == expected

def test_to_datetime_error():
    with pytest.raises(TypeError):
        to_datetime(sum)

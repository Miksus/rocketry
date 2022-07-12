from datetime import timedelta
import pytest
from rocketry.pybox.time import to_timedelta, to_datetime, Interval

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
        ('1  d 5  h 10  m 20  s', timedelta(days=1, hours=5, minutes=10, seconds=20)),
        ("1days 5hours 10minutes 20seconds", timedelta(days=1, hours=5, minutes=10, seconds=20)),
        ("1 day 5 hour 10 minute 20 second", timedelta(days=1, hours=5, minutes=10, seconds=20)),
        ("1 days 5 hours 10 minutes 20 seconds", timedelta(days=1, hours=5, minutes=10, seconds=20)),
        ("-1 days 5 hours 10 minutes 20 seconds", -timedelta(days=1, hours=5, minutes=10, seconds=20)),
        ("--1 days 5 hours 10 minutes 20 seconds", timedelta(days=1, hours=5, minutes=10, seconds=20)),
    ]
)
def test_timedelta(s, expected):
    assert to_timedelta(s) == expected


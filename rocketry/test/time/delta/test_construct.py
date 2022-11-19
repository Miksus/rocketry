
import datetime
import pytest
from rocketry.time import (
    TimeDelta, TimeOfDay
)

@pytest.mark.parametrize(
    "offset,expected",
    [
        pytest.param(
            "10:20:30",
            datetime.timedelta(hours=10, minutes=20, seconds=30),
            id="String"),
    ],
)
def test_construct(offset, expected):
    time = TimeDelta(offset)
    assert expected == time.past

def test_equal():
    assert TimeDelta("2 days") == TimeDelta("2 days")
    assert TimeDelta("2 days") != TimeDelta("3 days")
    assert TimeDelta("2 days") != TimeOfDay("10:00", "12:00")

def test_repr():
    assert str(TimeDelta("2 days")) == 'past 2 days, 0:00:00'
    assert str(TimeDelta(future="2 days")) == 'next 2 days, 0:00:00'
    assert str(TimeDelta(past="1 days", future="2 days")) == 'past 1 day, 0:00:00 to next 2 days, 0:00:00'
    assert repr(TimeDelta("2 days")) == "TimeDelta(past=datetime.timedelta(days=2), future=datetime.timedelta(0))"

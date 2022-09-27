
import datetime

from rocketry.time import (
    TimeSpanDelta
)


def test_construct():
    time = TimeSpanDelta("2:00:00", "3:00:00")
    assert time.near == datetime.timedelta(hours=2)
    assert time.far == datetime.timedelta(hours=3)

    time = TimeSpanDelta(near="2:00:00", far="3:00:00")
    assert time.near == datetime.timedelta(hours=2)
    assert time.far == datetime.timedelta(hours=3)

    time = TimeSpanDelta(near=datetime.timedelta(hours=2), far=datetime.timedelta(hours=3))
    assert time.near == datetime.timedelta(hours=2)
    assert time.far == datetime.timedelta(hours=3)

    time = TimeSpanDelta()
    assert time.near == datetime.timedelta(0)
    assert time.far is None

def test_equal():
    assert TimeSpanDelta("2 days") == TimeSpanDelta("2 days")
    assert TimeSpanDelta("2 days", "1 days") == TimeSpanDelta("2 days", "1 days")
    assert TimeSpanDelta("2 days") != TimeSpanDelta("3 days")
    assert TimeSpanDelta("2 days", "1 days") != TimeSpanDelta("3 days")
    assert TimeSpanDelta("1 days", "2 days") != TimeSpanDelta("5 hours", "2 days")

def test_repr():
    assert str(TimeSpanDelta("2 days"))
    assert repr(TimeSpanDelta("2 days"))

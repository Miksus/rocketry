
import datetime
import pytest
from rocketry.time import (
    TimeSpanDelta
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
    time = TimeSpanDelta(offset)
    assert expected == time.start
    assert 0 == time.end

def test_equal():
    assert TimeSpanDelta("2 days") == TimeSpanDelta("2 days")
    assert TimeSpanDelta("2 days", "1 days") == TimeSpanDelta("2 days", "1 days")
    assert not (TimeSpanDelta("2 days") == TimeSpanDelta("3 days"))
    assert not (TimeSpanDelta("2 days", "1 days") == TimeSpanDelta("3 days"))
    assert not (TimeSpanDelta("1 days", "2 days") == TimeSpanDelta("5 hours", "2 days"))

def test_repr():
    assert str(TimeSpanDelta("2 days"))
    assert repr(TimeSpanDelta("2 days"))
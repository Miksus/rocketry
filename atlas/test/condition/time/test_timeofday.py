from atlas.conditions import IsTimeOfDay

import datetime
from dateutil.parser import parse as parse_datetime

import pytest

class mockdatetime(datetime.datetime):
    _freezed_datetime = None
    @classmethod
    def now(cls):
        return cls._freezed_datetime

@pytest.fixture
def mock_datetime_now(monkeypatch):
    """Monkey patch datetime.datetime.now
    Returns a function that takes datetime as string as input
    and sets that to datetime.datetime.now()"""
    class mockdatetime(datetime.datetime):
        _freezed_datetime = None
        @classmethod
        def now(cls):
            return cls._freezed_datetime

    def wrapper(dt):
        mockdatetime._freezed_datetime = parse_datetime(dt)
        monkeypatch.setattr(datetime, 'datetime', mockdatetime)

    return wrapper


@pytest.mark.parametrize(
    "now,start,end,is_true",
    [
        pytest.param(
            "2020-01-01 10:00",
            "09:00", "12:00",
            True,
            id="In period"),
        pytest.param(
            "2020-01-01 08:00",
            "09:00", "12:00",
            False,
            id="Before period"),
        pytest.param(
            "2020-01-01 13:00",
            "09:00", "12:00",
            False,
            id="After period"),
        pytest.param(
            "2020-01-01 23:00",
            "22:00", "02:00",
            True,
            id="In period overnight before mid-night"),
        pytest.param(
            "2020-01-01 01:00",
            "22:00", "02:00",
            True,
            id="In period overnight after mid-night"),
        pytest.param(
            "2020-01-01 21:00",
            "22:00", "02:00",
            False,
            id="Before period overnight"),
        pytest.param(
            "2020-01-01 03:00",
            "22:00", "02:00",
            False,
            id="After period overnight"),
    ],
)
def test_time_of_day(mock_datetime_now, now, start, end, is_true):
    mock_datetime_now(now)
    
    cond = IsTimeOfDay(start, end)

    if is_true:
        assert bool(cond)
    else:
        assert not bool(cond)

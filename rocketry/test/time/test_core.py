import pytest

from rocketry.time.interval import (
    TimeOfHour,
    TimeOfDay,
)
from rocketry.time import All, Any, always

def test_equal():
    assert TimeOfHour("10:00") != TimeOfHour("11:00")
    assert TimeOfHour("10:00") == TimeOfHour("10:00")
    assert (TimeOfHour("10:00", "12:00") & TimeOfHour("11:00", "13:00")) == (TimeOfHour("10:00", "12:00") & TimeOfHour("11:00", "13:00"))
    assert (TimeOfHour("10:00", "12:00") | TimeOfHour("11:00", "13:00")) == (TimeOfHour("10:00", "12:00") | TimeOfHour("11:00", "13:00"))

def test_and():
    time = TimeOfHour("10:00", "14:00") & TimeOfHour("09:00", "12:00")
    assert time == All(TimeOfHour("10:00", "14:00"), TimeOfHour("09:00", "12:00"))

def test_and_reduce_always():
    time = always & always
    assert time is always

    time = TimeOfHour("10:00", "14:00") & always
    assert time == TimeOfHour("10:00", "14:00")


def test_any():
    time = TimeOfHour("10:00", "14:00") | TimeOfHour("09:00", "12:00")
    assert time == Any(TimeOfHour("10:00", "14:00"), TimeOfHour("09:00", "12:00"))

def test_any_reduce_always():
    time = always | always
    assert time is always

    time = TimeOfHour("10:00", "14:00") | always
    assert time is always

def test_error():
    with pytest.raises(ValueError):
        Any()
    with pytest.raises(ValueError):
        All()
    with pytest.raises(TypeError):
        Any(1, TimeOfHour())
    with pytest.raises(TypeError):
        All(1, TimeOfHour())

    # Test & and | don't work with non-period
    with pytest.raises(TypeError):
        TimeOfDay() & 1

    with pytest.raises(TypeError):
        TimeOfDay() | 1

def test_str():
    assert str(TimeOfDay("10:00", "12:00") & TimeOfDay("16:00", "17:00")) == '10 hours - 12 hours & 16 hours - 17 hours'
    assert str(TimeOfDay("10:00", "12:00") | TimeOfDay("16:00", "17:00")) == '10 hours - 12 hours | 16 hours - 17 hours'

def test_repr():
    assert repr(TimeOfDay("10:00", "12:00") & TimeOfDay("16:00", "17:00")) == 'All(TimeOfDay(_start=36000000000, _end=43200000000), TimeOfDay(_start=57600000000, _end=61200000000))'
    assert repr(TimeOfDay("10:00", "12:00") | TimeOfDay("16:00", "17:00")) == 'Any(TimeOfDay(_start=36000000000, _end=43200000000), TimeOfDay(_start=57600000000, _end=61200000000))'
